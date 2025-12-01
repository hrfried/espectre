"""
Micro-ESPectre - Main Application

Motion detection using WiFi CSI and MVS segmentation.
Main entry point for the Micro-ESPectre system running on ESP32-C6.

Author: Francesco Pace <francesco.pace@gmail.com>
License: GPLv3
"""
import network
import time
import gc
from src.segmentation import SegmentationContext
from src.mqtt.handler import MQTTHandler
from src.traffic_generator import TrafficGenerator
from src.nvs_storage import NVSStorage
from src.nbvi_calibrator import NBVICalibrator
import src.config as config

# Try to import local configuration (overrides config.py defaults)
try:
    from config_local import WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD
    # Override config with local settings
    config.MQTT_BROKER = MQTT_BROKER
    config.MQTT_PORT = MQTT_PORT
    config.MQTT_USERNAME = MQTT_USERNAME
    config.MQTT_PASSWORD = MQTT_PASSWORD
except ImportError:
    WIFI_SSID = config.WIFI_SSID
    WIFI_PASSWORD = config.WIFI_PASSWORD


# Global state for calibration mode
class GlobalState:
    def __init__(self):
        self.calibration_mode = False  # Flag to suspend main loop during calibration


g_state = GlobalState()


def connect_wifi():
    """Connect to WiFi"""
    
    print(f"Connecting to WiFi...")
    
    gc.collect()
    wlan = network.WLAN(network.STA_IF)
    
    # Initialize WiFi
    if wlan.active():
        wlan.active(False)
    wlan.active(True)
    
    if not wlan.active():
        raise Exception("WiFi failed to activate")
    
    # Disable power save for CSI stability
    wlan.config(pm=wlan.PM_NONE)
    
    # Disconnect if already connected
    if wlan.isconnected():
        wlan.disconnect()
    
    # Wait for hardware initialization
    time.sleep(2)  
    
    # Connect
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # Wait for connection
    timeout = 30
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print(f"✅ WiFi connected - IP: {wlan.ifconfig()[0]}")
        time.sleep(1)  # Stabilization
        return wlan
    else:
        raise Exception("Connection timeout")


def format_progress_bar(score, threshold, width=20):
    """Format progress bar for console output"""
    threshold_pos = 15
    filled = int(score * threshold_pos)
    filled = max(0, min(filled, width))
    
    bar = '['
    for i in range(width):
        if i == threshold_pos:
            bar += '|'
        elif i < filled:
            bar += '█'
        else:
            bar += '░'
    bar += ']'
    
    percent = int(score * 100)
    return f"{bar} {percent}%"


def run_nbvi_calibration(wlan, nvs, seg, traffic_gen):
    """
    Run NBVI calibration
    
    Args:
        wlan: WLAN instance
        nvs: NVSStorage instance
        seg: SegmentationContext instance
        traffic_gen: TrafficGenerator instance
    
    Returns:
        bool: True if calibration successful
    """
    # Set calibration mode to suspend main loop
    g_state.calibration_mode = True
    
    print('')
    print('='*60)
    print('🧬 NBVI Auto-Calibration Starting')
    print('='*60)
    print('Please remain still for 10 seconds...')
    print('Collecting CSI data for automatic subcarrier selection')
    print('')
    
    # Initialize NBVI calibrator
    nbvi_calibrator = NBVICalibrator(
        buffer_size=config.NBVI_BUFFER_SIZE,
        percentile=config.NBVI_PERCENTILE,
        alpha=config.NBVI_ALPHA,
        min_spacing=config.NBVI_MIN_SPACING
    )
    
    # Collect packets for calibration
    print("NBVI: Starting packet collection loop...")
    calibration_progress = 0
    timeout_counter = 0
    max_timeout = 15000  # 15 seconds
    packets_read = 0
    
    while calibration_progress < config.NBVI_BUFFER_SIZE:
        frame = wlan.csi_read()
        packets_read += 1
        
        if frame:
            csi_data = frame[5][:128]  # frame[5] = data (tuple API)
            calibration_progress = nbvi_calibrator.add_packet(csi_data)
            timeout_counter = 0  # Reset timeout on successful read
            
            # Print progress every 100 packets
            if calibration_progress % 100 == 0:
                print(f"NBVI: Collecting {calibration_progress}/{config.NBVI_BUFFER_SIZE} packets... (read attempts: {packets_read})")
                gc.collect()  # Garbage collect during progress
        else:
            time.sleep_ms(1)
            timeout_counter += 1
            
            # Debug: print if stuck
            if timeout_counter % 1000 == 0:
                # Check if traffic generator is still running
                tg_running = traffic_gen.is_running()
                tg_count = traffic_gen.get_packet_count()
                dropped = wlan.csi_dropped()
                print(f"NBVI: Waiting for CSI... ({timeout_counter/1000:.0f}s, progress: {calibration_progress}, TG running: {tg_running}, TG packets: {tg_count}, dropped: {dropped})")
            
            if timeout_counter >= max_timeout:
                print(f"NBVI: Timeout waiting for CSI packets (collected {calibration_progress}/{config.NBVI_BUFFER_SIZE})")
                print("NBVI: Calibration aborted - using default band")
                return False
    
    print(f"NBVI: Collection complete ({config.NBVI_BUFFER_SIZE} packets)")
    
    # Calibrate using percentile-based approach
    success = False
    try:
        selected_band = nbvi_calibrator.calibrate(config.SELECTED_SUBCARRIERS)
        
        if selected_band and len(selected_band) == 12:
            # Calibration successful
            config.SELECTED_SUBCARRIERS = selected_band
            success = True
            
            print('')
            print('='*60)
            print('✅ NBVI Calibration Successful!')
            print(f'   Selected band: {selected_band}')
            print('   Configuration saved to NVS')
            print('='*60)
            print('')
        else:
            # Calibration failed - keep default
            print('')
            print('='*60)
            print('⚠️  NBVI Calibration Failed')
            print(f'   Using default band: {config.SELECTED_SUBCARRIERS}')
            print('='*60)
            print('')
    
    except Exception as e:
        print(f"NBVI: Error during calibration: {e}")
        print(f"NBVI: Using default band: {config.SELECTED_SUBCARRIERS}")
    
    # Free calibrator memory
    nbvi_calibrator = None
    gc.collect()
    
    # Save configuration
    nvs.save_full_config(seg, config)
    
    # Resume main loop
    g_state.calibration_mode = False
    
    return success




def main():
    """Main application loop"""
    print('Micro-ESPectre starting...')
    
    # Connect to WiFi
    wlan = connect_wifi()
    
    # Configure and enable CSI
    wlan.csi_enable(buffer_size=config.CSI_BUFFER_SIZE)
    
    # Initialize segmentation
    seg = SegmentationContext(
        window_size=config.SEG_WINDOW_SIZE,
        threshold=config.SEG_THRESHOLD
    )
    
    # Load saved configuration
    nvs = NVSStorage()
    saved_config = nvs.load_and_apply(seg, config)
    
    # Initialize and start traffic generator
    traffic_gen = TrafficGenerator()
    traffic_rate = config.TRAFFIC_GENERATOR_RATE
    if saved_config and "traffic_generator" in saved_config:
        traffic_rate = saved_config["traffic_generator"].get("rate", traffic_rate)
    
    if traffic_rate > 0:
        traffic_gen.start(traffic_rate)
        print(f'📡 Traffic generator started ({traffic_rate} pps)')
        time.sleep(1)  # Wait for traffic to start generating CSI packets
    
    # NBVI Auto-Calibration at boot (if enabled and needed)
    if config.NBVI_ENABLED and not saved_config:
        run_nbvi_calibration(wlan, nvs, seg, traffic_gen)
    else:
        print('🧬 NBVI: Auto-calibration disabled or already calibrated')
    
    # Initialize MQTT (pass calibration function for factory_reset)
    mqtt_handler = MQTTHandler(config, seg, wlan, traffic_gen, run_nbvi_calibration)
    mqtt_handler.connect()
    
    # Publish info after boot (always, to show current configuration)
    print('📡 Publishing system info...')
    mqtt_handler.publish_info()
    
    print('')
    print('╔═══════════════════════════════════════════════════════════╗')
    print('║                   🛜  Micro - ESPectre 👻                  ║')
    print('║                                                           ║')
    print('║                Wi-Fi motion detection system              ║')
    print('║          based on Channel State Information (CSI)         ║')
    print('║                                                           ║')
    print('╠═══════════════════════════════════════════════════════════╣')
    print('║                                                           ║')
    print('║             System Ready - Monitoring Active              ║')
    print('║               Detecting the invisible... 👁️                ║')
    print('║                                                           ║')
    print('╚═══════════════════════════════════════════════════════════╝')
    print('')
    
    # Main CSI processing loop with integrated MQTT publishing
    packet_counter = 0
    packets_since_publish = 0
    last_dropped = 0
    last_publish_time = time.ticks_ms()
    
    # Calculate optimal sleep based on traffic rate
    traffic_rate = traffic_gen.get_rate() if traffic_gen.is_running() else 100
    publish_rate = traffic_rate
       
    try:
        while True:
            # Suspend main loop during calibration
            if g_state.calibration_mode:
                time.sleep_ms(100)
                continue
            
            # Check MQTT messages (non-blocking)
            mqtt_handler.check_messages()
            
            frame = wlan.csi_read()
            
            if frame:
                # ESP32-C6 provides 512 bytes but we use only first 128 bytes
                # This avoids corrupted data in the extended buffer
                csi_data = frame[5][:128]  # frame[5] = data (tuple API)
                turbulence = seg.calculate_spatial_turbulence(csi_data, config.SELECTED_SUBCARRIERS)
                seg.add_turbulence(turbulence)
                metrics = seg.get_metrics()
                
                packets_since_publish += 1
                
                # Publish every N packets (where N = traffic_rate)
                if packets_since_publish >= publish_rate:
                    current_time = time.ticks_ms()
                    time_delta = time.ticks_diff(current_time, last_publish_time)
                    
                    # Calculate packets per second
                    pps = int((packets_since_publish * 1000) / time_delta) if time_delta > 0 else 0
                    
                    dropped = wlan.csi_dropped()
                    dropped_delta = dropped - last_dropped
                    last_dropped = dropped
                    
                    state_str = 'MOTION' if metrics['state'] == 1 else 'IDLE'
                    progress = metrics['moving_variance'] / metrics['threshold'] if metrics['threshold'] > 0 else 0
                    progress_bar = format_progress_bar(progress, metrics['threshold'])
                    print(f"📊 {progress_bar} | pkts:{packets_since_publish} drop:{dropped_delta} pps:{pps} | "
                          f"mvmt:{metrics['moving_variance']:.4f} thr:{metrics['threshold']:.4f} | {state_str}")
                    
                    mqtt_handler.publish_state(
                        metrics['moving_variance'],
                        metrics['state'],
                        metrics['threshold'],
                        packets_since_publish,
                        dropped_delta
                    )
                    
                    packets_since_publish = 0
                    last_publish_time = current_time
                
                # Periodic garbage collection (every 100 packets)
                packet_counter += 1
                if packet_counter >= 100:
                    gc.collect()
                    packet_counter = 0
                
            else:
                time.sleep_us(10)  # Small sleep to yield CPU
    
    except KeyboardInterrupt:
        print('\n\nStopping...')
    
    finally:
        wlan.csi_disable()
        mqtt_handler.disconnect()        
        if traffic_gen.is_running():
            traffic_gen.stop()

if __name__ == '__main__':
    main()
