"""
Micro-ESPectre - MQTT Commands Module

Processes MQTT commands for remote configuration.
Handles system configuration, calibration, and status queries via MQTT.

Author: Francesco Pace <francesco.pace@gmail.com>
License: GPLv3
"""
import json
import time
import gc
import sys
from src.nvs_storage import NVSStorage
from src.config import (
    TRAFFIC_RATE_MIN, TRAFFIC_RATE_MAX, TRAFFIC_GENERATOR_RATE,
    SEG_WINDOW_SIZE, SEG_THRESHOLD,
    SEG_WINDOW_SIZE_MIN, SEG_WINDOW_SIZE_MAX,
    SEG_THRESHOLD_MIN, SEG_THRESHOLD_MAX,
    SUBCARRIER_INDEX_MIN, SUBCARRIER_INDEX_MAX,
    SELECTED_SUBCARRIERS
)


class MQTTCommands:
    """MQTT command processor"""
    
    def __init__(self, mqtt_client, config, segmentation, response_topic, wlan, traffic_generator=None, nbvi_calibration_func=None):
        """
        Initialize MQTT commands
        
        Args:
            mqtt_client: MQTT client instance
            config: Configuration module
            segmentation: SegmentationContext instance
            response_topic: MQTT topic for responses
            wlan: wlan instance
            traffic_generator: TrafficGenerator instance (optional)
            nbvi_calibration_func: Function to run NBVI calibration (optional)
        """
        self.mqtt = mqtt_client
        self.config = config
        self.seg = segmentation
        self.wlan = wlan
        self.traffic_gen = traffic_generator
        self.nbvi_calibration_func = nbvi_calibration_func
        self.response_topic = response_topic
        self.start_time = time.time()
        
        # NVS storage for configuration persistence
        self.nvs = NVSStorage()
        
    def send_response(self, message):
        """Send response message to MQTT"""
        try:
            # If message is a dict, convert to JSON
            if isinstance(message, dict):
                message = json.dumps(message)
            else:
                # If message is plain text, check if it's already valid JSON
                try:
                    json.loads(message)
                    # Already valid JSON, send as-is
                except (ValueError, TypeError):
                    # Plain text message, wrap in {"response": "..."}
                    message = json.dumps({"response": message})
            
            self.mqtt.publish(self.response_topic, message)
        except Exception as e:
            print(f"Error sending MQTT response: {e}")
    
    def format_uptime(self, uptime_sec):
        """Format uptime as human-readable string"""
        hours = int(uptime_sec // 3600)
        minutes = int((uptime_sec % 3600) // 60)
        seconds = int(uptime_sec % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def cmd_info(self):
        """Get system information"""
        # Get WiFi info
        ip_address = "not connected"
        mac_address = "unknown"
        channel_primary = 0
        channel_secondary = 0
        bandwidth = "unknown"
        protocol = "unknown"
        promiscuous = False
        
        if self.wlan.active():
            # MAC address
            mac_bytes = self.wlan.config('mac')
            mac_address = ':'.join(['%02X' % b for b in mac_bytes])
            
            # IP address
            if self.wlan.isconnected():
                ip_info = self.wlan.ifconfig()
                ip_address = ip_info[0] if ip_info else "unknown"
            
            # WiFi channel
            try:
                channel_primary = self.wlan.config('channel')
                # MicroPython doesn't expose secondary channel directly
                channel_secondary = 0
            except:
                pass
            
            # WiFi bandwidth (MicroPython typically uses HT20)
            bandwidth = "-" #TODO: detect actual bandwidth
            
            # WiFi protocol (MicroPython supports 802.11b/g/n)
            protocol = "-" #TODO: detect actual protocol
            
            # Promiscuous mode (not typically exposed in MicroPython)
            promiscuous = False #TODO: detect actual protocol
        
        # Get traffic generator rate (current runtime value)
        traffic_rate = 0
        if self.traffic_gen:
            traffic_rate = self.traffic_gen.get_rate()
        
        response = {
            "network": {
                "ip_address": ip_address,
                "mac_address": mac_address,
                "traffic_generator_rate": traffic_rate,
                "channel": {
                    "primary": channel_primary,
                    "secondary": channel_secondary
                },
                "bandwidth": bandwidth,
                "protocol": protocol,
                "promiscuous_mode": promiscuous
            },
            "device": {
                "type": sys.platform
            },
            "mqtt": {
                "base_topic": self.config.MQTT_TOPIC,
                "cmd_topic": f"{self.config.MQTT_TOPIC}/cmd",
                "response_topic": self.response_topic
            },
            "segmentation": {
                "threshold": round(self.seg.threshold, 2),
                "window_size": self.seg.window_size
            },
            "subcarriers": {
                "indices": self.config.SELECTED_SUBCARRIERS,
                "count": len(self.config.SELECTED_SUBCARRIERS)
            }
        }
        
        self.send_response(response)
        print("📋 Info command processed")
    
    def cmd_stats(self):
        """Get runtime statistics"""
        current_time = time.time()
        uptime_sec = current_time - self.start_time
        
        # Get memory info using ESP32 IDF heap info for more accurate data
        gc.collect()
        heap_usage = 0.0
        try:
            import esp32
            # Get detailed heap info for DATA regions (where MicroPython heap lives)
            heap_regions = esp32.idf_heap_info(esp32.HEAP_DATA)
            
            # Sum up total and free bytes across all DATA heap regions
            total_bytes = 0
            free_bytes = 0
            for region in heap_regions:
                total, free, largest_block, min_free = region
                total_bytes += total
                free_bytes += free
            
            # Calculate usage percentage
            if total_bytes > 0:
                used_bytes = total_bytes - free_bytes
                heap_usage = (used_bytes / total_bytes * 100.0)
        except:
            # Fallback to gc module if esp32.idf_heap_info is not available
            free_mem = gc.mem_free()
            alloc_mem = gc.mem_alloc()
            total_mem = free_mem + alloc_mem
            heap_usage = (alloc_mem / total_mem * 100.0) if total_mem > 0 else 0.0
        
        # Calculate CPU usage using FreeRTOS task info
        cpu_usage = None
        try:
            import esp32
            # Get task runtime statistics
            total_runtime, tasks = esp32.idf_task_info()
            
            if total_runtime and total_runtime > 0:
                # Calculate total CPU time used (excluding IDLE tasks)
                cpu_time = 0
                for task in tasks:
                    task_id, name, state, priority, runtime, stack_hwm, core_id = task
                    # Skip IDLE tasks (they represent unused CPU time)
                    if runtime and 'IDLE' not in name:
                        cpu_time += runtime
                
                # CPU usage = (non-idle time / total time) * 100
                cpu_usage = (cpu_time / total_runtime * 100.0) if total_runtime > 0 else 0.0
                cpu_usage = min(100.0, max(0.0, cpu_usage))  # Clamp to 0-100%
        except Exception as e:
            # esp32.idf_task_info() not available or failed
            # This can happen if CONFIG_FREERTOS_USE_TRACE_FACILITY is not enabled
            # Don't send cpu_usage_percent in response
            pass
        
        # Get current state
        state_str = 'motion' if self.seg.state == self.seg.STATE_MOTION else 'idle'
        
        # Build response - only include cpu_usage_percent if available
        response = {
            "timestamp": int(current_time),
            "uptime": self.format_uptime(uptime_sec),
            "heap_usage_percent": round(heap_usage, 1),
            "state": state_str,
            "turbulence": round(self.seg.last_turbulence, 4),
            "movement": round(self.seg.current_moving_variance, 4),
            "threshold": round(self.seg.threshold, 4)
        }
        
        # Add CPU usage only if available
        if cpu_usage is not None:
            response["cpu_usage_percent"] = round(cpu_usage, 1)
        
        self.send_response(response)
        print("📊 Stats command processed")
    
    def cmd_segmentation_threshold(self, cmd_obj):
        """Set segmentation threshold"""
        if 'value' not in cmd_obj:
            self.send_response("ERROR: Missing 'value' field")
            return
        
        try:
            threshold = float(cmd_obj['value'])
            
            if threshold < SEG_THRESHOLD_MIN or threshold > SEG_THRESHOLD_MAX:
                self.send_response(f"ERROR: Threshold must be between {SEG_THRESHOLD_MIN} and {SEG_THRESHOLD_MAX}")
                return
            
            old_threshold = self.seg.threshold
            self.seg.threshold = threshold
            
            # Save to NVS
            self.nvs.save_full_config(self.seg, self.config, self.traffic_gen)
            
            self.send_response(f"Segmentation threshold updated: {old_threshold:.2f} -> {threshold:.2f}")
            print(f"📍 Threshold updated: {old_threshold:.2f} -> {threshold:.2f}")
            
        except ValueError:
            self.send_response("ERROR: Invalid threshold value (must be float)")
    
    def cmd_segmentation_window_size(self, cmd_obj):
        """Set window size"""
        if 'value' not in cmd_obj:
            self.send_response("ERROR: Missing 'value' field")
            return
        
        try:
            window_size = int(cmd_obj['value'])
            
            if window_size < SEG_WINDOW_SIZE_MIN or window_size > SEG_WINDOW_SIZE_MAX:
                self.send_response(f"ERROR: Window size must be between {SEG_WINDOW_SIZE_MIN} and {SEG_WINDOW_SIZE_MAX} packets")
                return
            
            old_size = self.seg.window_size
            
            # Update window size and reset buffer
            self.seg.window_size = window_size
            self.seg.turbulence_buffer = [0.0] * window_size
            self.seg.buffer_index = 0
            self.seg.buffer_count = 0
            self.seg.current_moving_variance = 0.0
            
            # Save to NVS
            self.nvs.save_full_config(self.seg, self.config, self.traffic_gen)
            
            # Calculate duration using actual traffic rate
            rate = self.traffic_gen.get_rate() if self.traffic_gen else TRAFFIC_GENERATOR_RATE
            duration = window_size / rate if rate > 0 else 0.0
            reactivity = "more reactive" if window_size < (SEG_WINDOW_SIZE_MAX // 2) else "more stable"
            self.send_response(f"Window size updated: {old_size} -> {window_size} packets ({duration:.2f}s @ {rate}Hz, {reactivity})")
            print(f"📍 Window size updated: {old_size} -> {window_size} (buffer reset)")
            
        except ValueError:
            self.send_response("ERROR: Invalid window size value (must be integer)")
    
    def cmd_subcarrier_selection(self, cmd_obj):
        """Set subcarrier selection"""
        if 'indices' not in cmd_obj:
            self.send_response("ERROR: Missing 'indices' field")
            return
        
        try:
            indices = cmd_obj['indices']
            
            if not isinstance(indices, list):
                self.send_response("ERROR: 'indices' must be an array")
                return
            
            if len(indices) < 1 or len(indices) > (SUBCARRIER_INDEX_MAX + 1):
                self.send_response(f"ERROR: Number of subcarriers must be between 1 and {SUBCARRIER_INDEX_MAX + 1}")
                return
            
            # Validate all indices
            for idx in indices:
                if not isinstance(idx, int) or idx < SUBCARRIER_INDEX_MIN or idx > SUBCARRIER_INDEX_MAX:
                    self.send_response(f"ERROR: Subcarrier index {idx} out of range (must be {SUBCARRIER_INDEX_MIN}-{SUBCARRIER_INDEX_MAX})")
                    return
            
            # Update configuration
            self.config.SELECTED_SUBCARRIERS = indices
            
            # Save to NVS
            self.nvs.save_full_config(self.seg, self.config, self.traffic_gen)
            
            self.send_response(f"Subcarrier selection updated: {len(indices)} subcarriers")
            print(f"📡 Subcarrier selection updated: {len(indices)} subcarriers")
            
        except Exception as e:
            self.send_response(f"ERROR: Invalid subcarrier selection: {e}")
    
    def cmd_factory_reset(self, cmd_obj):
        """Reset all parameters to defaults and trigger NBVI re-calibration"""
        print("⚠️  Factory reset requested")
        
        # Reset segmentation to defaults (use constants from config.py)
        self.seg.threshold = SEG_THRESHOLD
        self.seg.window_size = SEG_WINDOW_SIZE
        
        # Reset buffer
        self.seg.turbulence_buffer = [0.0] * self.seg.window_size
        self.seg.buffer_index = 0
        self.seg.buffer_count = 0
        self.seg.current_moving_variance = 0.0
        
        # Reset state machine
        self.seg.state = self.seg.STATE_IDLE
        self.seg.packet_index = 0
        
        # Reset subcarrier selection to defaults
        self.config.SELECTED_SUBCARRIERS = SELECTED_SUBCARRIERS.copy()
        
        # Reset traffic generator to default rate
        if self.traffic_gen:
            if TRAFFIC_GENERATOR_RATE > 0:
                if self.traffic_gen.is_running():
                    # Just change the rate
                    if self.traffic_gen.set_rate(TRAFFIC_GENERATOR_RATE):
                        print(f"📡 Traffic generator rate reset to default ({TRAFFIC_GENERATOR_RATE} pps)")
                    else:
                        print("⚠️  Failed to reset traffic generator rate")
                else:
                    # Start with default rate
                    if self.traffic_gen.start(TRAFFIC_GENERATOR_RATE):
                        print(f"📡 Traffic generator started at default rate ({TRAFFIC_GENERATOR_RATE} pps)")
                    else:
                        print("⚠️  Failed to start traffic generator")
            elif self.traffic_gen.is_running():
                # Default rate is 0, stop traffic generator
                self.traffic_gen.stop()
                print("📡 Traffic generator stopped (default rate is 0)")
        
        # Erase saved configuration
        self.nvs.erase()

        print("✅ Factory reset complete")
        
        # Run NBVI calibration immediately if function provided
        if self.nbvi_calibration_func:
            self.send_response("Factory reset complete. Starting NBVI re-calibration...")
            print("🧬 Starting NBVI re-calibration...")
            
            # Run calibration
            success = self.nbvi_calibration_func(self.wlan, self.nvs, self.seg, self.traffic_gen)
            
            if success:
                self.send_response(f"NBVI re-calibration successful! Band: {self.config.SELECTED_SUBCARRIERS}")
            else:
                self.send_response(f"NBVI re-calibration failed. Using default band.")
        else:
            self.send_response(f"Factory reset complete.")
    
    def cmd_traffic_generator_rate(self, cmd_obj):
        """Set traffic generator rate"""
        if not self.traffic_gen:
            self.send_response("ERROR: Traffic generator not available")
            return
        
        if 'value' not in cmd_obj:
            self.send_response("ERROR: Missing 'value' field")
            return
        
        try:
            rate = int(cmd_obj['value'])
            
            if rate < TRAFFIC_RATE_MIN or rate > TRAFFIC_RATE_MAX:
                self.send_response(f"ERROR: Rate must be {TRAFFIC_RATE_MIN}-{TRAFFIC_RATE_MAX} packets/sec (0=disabled, {TRAFFIC_GENERATOR_RATE} recommended)")
                return
            
            old_rate = self.traffic_gen.get_rate()
            
            if rate == 0:
                # Disable traffic generator
                if self.traffic_gen.is_running():
                    self.traffic_gen.stop()
                    self.send_response(f"Traffic generator disabled (was {old_rate} pps)")
                    print(f"📡 Traffic generator disabled")
                else:
                    self.send_response("Traffic generator already disabled")
            else:
                # Enable or change rate
                if self.traffic_gen.is_running():
                    # Change rate
                    if self.traffic_gen.set_rate(rate):
                        # Save to NVS
                        self.nvs.save_full_config(self.seg, self.config, self.traffic_gen)
                        self.send_response(f"Traffic rate updated: {old_rate} -> {rate} pps")
                        print(f"📡 Traffic rate changed to {rate} pps")
                    else:
                        self.send_response("ERROR: Failed to change traffic rate")
                else:
                    # Start traffic generator
                    if self.traffic_gen.start(rate):
                        # Save to NVS
                        self.nvs.save_full_config(self.seg, self.config, self.traffic_gen)
                        self.send_response(f"Traffic generator enabled ({rate} pps)")
                    else:
                        self.send_response("ERROR: Failed to start traffic generator")
                        
        except ValueError:
            self.send_response("ERROR: Invalid rate value (must be integer)")
    
    def process_command(self, data):
        """
        Process incoming MQTT command
        
        Args:
            data: Command data (bytes or string)
        """
        try:
            # Parse JSON command
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            cmd_obj = json.loads(data)
            
            if 'cmd' not in cmd_obj:
                self.send_response("ERROR: Missing 'cmd' field")
                return
            
            command = cmd_obj['cmd']
            print(f"Processing MQTT command: {command}")
            
            # Dispatch command
            if command == 'info':
                self.cmd_info()
            elif command == 'stats':
                self.cmd_stats()
            elif command == 'segmentation_threshold':
                self.cmd_segmentation_threshold(cmd_obj)
            elif command == 'segmentation_window_size':
                self.cmd_segmentation_window_size(cmd_obj)
            elif command == 'subcarrier_selection':
                self.cmd_subcarrier_selection(cmd_obj)
            elif command == 'factory_reset':
                self.cmd_factory_reset(cmd_obj)
            elif command == 'traffic_generator_rate':
                self.cmd_traffic_generator_rate(cmd_obj)
            else:
                self.send_response(f"ERROR: Unknown command '{command}'")
                
        except Exception as e:
            error_msg = f"ERROR: Command processing failed: {e}"
            print(error_msg)
            self.send_response(error_msg)
