# 🛜 ESPectre 👻 - Setup Guide

Complete guide to install and configure ESPectre with ESPHome.

---

## What You Need

---

**Hardware:**
- **ESP32-S3:** or **ESP32-C6:**
- USB-C or Micro-USB cable (depending on board)
- Wi-Fi router (2.4 GHz, 802.11b|g|n|ax)

**Software:**
- Python 3.12 or newer
- ESPHome 2024.x or newer
- Home Assistant (recommended, but optional)

---

## Installation

---

### Option 1: ESPHome Dashboard (Recommended)

If you have Home Assistant with ESPHome add-on installed:

1. Open **ESPHome Dashboard** in Home Assistant
2. Click **+ NEW DEVICE**
3. Choose **Continue** → **Skip this step** (we'll use manual YAML)
4. Create a new file named `espectre.yaml`
5. Copy the configuration below
6. Click **Install** → **Plug into this computer** (first time) or **Wirelessly** (after first flash)

### Option 2: Standalone ESPHome (Command Line)

**Install ESPHome:**

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install ESPHome
pip install esphome
```

**Create secrets file:**

Create a `secrets.yaml` file in the same directory as your configuration:

```yaml
# secrets.yaml
wifi_ssid: "YourWiFiName"
wifi_password: "YourWiFiPassword"
```

**Create configuration:**

Create `espectre.yaml` with the configuration below.

**Build and flash:**

```bash
# Compile and upload (first time - USB cable required)
esphome run espectre.yaml

# After first flash, you can update wirelessly (OTA)
esphome run espectre.yaml
```

---

## Configuration

---

### Minimal Configuration

```yaml
esphome:
  name: espectre

esp32:
  variant: ESP32C6  # or ESP32S3
  framework:
    type: esp-idf
    version: 5.4.2
    sdkconfig_options:
      CONFIG_ESP_WIFI_CSI_ENABLED: y
      CONFIG_PM_ENABLE: n

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  power_save_mode: NONE

api:  # Home Assistant integration

ota:
  - platform: esphome

logger:
  level: INFO

external_components:
  - source: github://francescopace/espectre
    components: [ espectre ]

espectre:
  traffic_generator_rate: 100
  segmentation_threshold: 1.0

binary_sensor:
  - platform: espectre
    motion:
      name: "Motion Detected"
      device_class: motion

sensor:
  - platform: espectre
    movement:
      name: "Movement Score"
    threshold:
      name: "Detection Threshold"
```

### Full Configuration (All Options)

```yaml
esphome:
  name: espectre

esp32:
  variant: ESP32C6
  framework:
    type: esp-idf
    version: 5.4.2
    sdkconfig_options:
      # Required for CSI
      CONFIG_ESP_WIFI_CSI_ENABLED: y
      CONFIG_PM_ENABLE: n
      CONFIG_ESP_WIFI_STA_DISCONNECTED_PM_ENABLE: n
      # Recommended for better performance
      CONFIG_ESP_WIFI_AMPDU_TX_ENABLED: n
      CONFIG_ESP_WIFI_AMPDU_RX_ENABLED: y
      CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM: '16'
      CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM: '64'
      CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM: '64'
      CONFIG_ESP_WIFI_RX_BA_WIN: '32'
      # Optional: IRAM optimization for faster processing
      CONFIG_ESP_WIFI_IRAM_OPT: y
      CONFIG_ESP_WIFI_RX_IRAM_OPT: y

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  power_save_mode: NONE

api:  # Home Assistant integration

web_server:
  port: 80  # Optional: HTTP endpoint for debugging

ota:
  - platform: esphome

logger:
  level: INFO
  logs:
    sensor: WARN         # Reduce sensor state logging
    binary_sensor: WARN  # Reduce binary sensor state logging

external_components:
  - source: github://francescopace/espectre
    components: [ espectre ]

espectre:
  # Traffic generator (ESSENTIAL for CSI!)
  traffic_generator_rate: 100   # Packets/sec (0-1000, 0=disabled)
  
  # Motion detection
  segmentation_threshold: 1.0   # Sensitivity (0.5-10.0, lower=more sensitive)
  segmentation_window_size: 50  # Moving variance window (10-200 packets)
  
  # Subcarrier selection (omit for auto-calibration)
  # selected_subcarriers: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
  
  # Feature extraction (optional)
  features_enabled: false       # Enable for ML analysis
  
  # Features processing filters (only if features_enabled: true)
  butterworth_enabled: false    # Low-pass filter (removes noise >8Hz)
  savgol_enabled: false         # Savitzky-Golay polynomial smoothing
  hampel_enabled: false         # Outlier removal using MAD
  hampel_threshold: 2.0         # MAD multiplier (1.0-10.0)
  wavelet_enabled: false        # Wavelet transform denoising
  wavelet_level: 3              # Wavelet decomposition depth (1-3)
  wavelet_threshold: 1.0        # Wavelet noise threshold (0.5-2.0)

binary_sensor:
  - platform: espectre
    motion:
      name: "Motion Detected"
      device_class: motion

sensor:
  - platform: espectre
    # Core sensors
    movement:
      name: "Movement Score"
    threshold:
      name: "Detection Threshold"
    
    # Feature sensors (only if features_enabled: true)
    # variance:
    #   name: "CSI Variance"
    # skewness:
    #   name: "CSI Skewness"
    # kurtosis:
    #   name: "CSI Kurtosis"
    # entropy:
    #   name: "CSI Entropy"
    # iqr:
    #   name: "CSI IQR"
    # spatial_variance:
    #   name: "Spatial Variance"
    # spatial_correlation:
    #   name: "Spatial Correlation"
    # spatial_gradient:
    #   name: "Spatial Gradient"
    # temporal_delta_mean:
    #   name: "Temporal Delta Mean"
    # temporal_delta_variance:
    #   name: "Temporal Delta Variance"
```

---

## Configuration Parameters

---

### ESPectre Component

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `traffic_generator_rate` | int | 100 | 0-1000 | Packets/sec for CSI generation (0=disabled) |
| `segmentation_threshold` | float | 1.0 | 0.5-10.0 | Motion sensitivity (lower=more sensitive) |
| `segmentation_window_size` | int | 50 | 10-200 | Moving variance window in packets |
| `selected_subcarriers` | list | auto | 0-63 | Fixed subcarriers (omit for auto-calibration) |
| `features_enabled` | bool | false | - | Enable statistical feature extraction |
| `butterworth_enabled` | bool | false | - | Enable Butterworth low-pass filter |
| `savgol_enabled` | bool | false | - | Enable Savitzky-Golay smoothing |
| `hampel_enabled` | bool | false | - | Enable Hampel outlier filter |
| `hampel_threshold` | float | 2.0 | 1.0-10.0 | Hampel filter sensitivity |
| `wavelet_enabled` | bool | false | - | Enable wavelet denoising |
| `wavelet_level` | int | 3 | 1-3 | Wavelet decomposition depth |
| `wavelet_threshold` | float | 1.0 | 0.5-2.0 | Wavelet noise threshold |

### Binary Sensor

| Sensor | Description |
|--------|-------------|
| `motion` | Motion detected (on/off) |

### Numeric Sensors

| Sensor | Description |
|--------|-------------|
| `movement` | Current motion intensity value |
| `threshold` | Active detection threshold |
| `turbulence` | Signal turbulence (optional) |
| `variance` | CSI variance (requires features_enabled) |
| `skewness` | CSI skewness (requires features_enabled) |
| `kurtosis` | CSI kurtosis (requires features_enabled) |
| `entropy` | CSI entropy (requires features_enabled) |
| `iqr` | CSI interquartile range (requires features_enabled) |
| `spatial_variance` | Spatial variance (requires features_enabled) |
| `spatial_correlation` | Spatial correlation (requires features_enabled) |
| `spatial_gradient` | Spatial gradient (requires features_enabled) |
| `temporal_delta_mean` | Temporal delta mean (requires features_enabled) |
| `temporal_delta_variance` | Temporal delta variance (requires features_enabled) |

---

## Home Assistant Integration

---

ESPHome provides **automatic Home Assistant integration**. Once the device is flashed and connected to WiFi:

1. Home Assistant will automatically discover the device
2. Go to **Settings** → **Devices & Services** → **ESPHome**
3. Click **Configure** on the discovered device
4. All sensors will be automatically added

### Entities Created

After integration, you'll have:

- **binary_sensor.espectre_motion_detected** - Motion state (on/off)
- **sensor.espectre_movement_score** - Movement intensity value
- **sensor.espectre_detection_threshold** - Current threshold

### Automation Examples

**Motion-triggered light:**

```yaml
automation:
  - alias: "Turn on light on motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.espectre_motion_detected
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room

  - alias: "Turn off light after no motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.espectre_motion_detected
        to: "off"
        for:
          minutes: 5
    action:
      - service: light.turn_off
        target:
          entity_id: light.living_room
```

**Inactivity alert:**

```yaml
automation:
  - alias: "Inactivity Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.espectre_motion_detected
        to: "off"
        for:
          hours: 4
    condition:
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: "No movement detected for 4 hours"
```

---

## Traffic Generator

---

**⚠️ IMPORTANT:** The traffic generator is **ESSENTIAL** for CSI packet generation. Without it, the ESP32 receives zero CSI packets and detection will not work.

### What it does

- Generates UDP broadcast packets at configurable rate
- Each packet triggers a CSI callback from the WiFi driver
- Ensures continuous CSI data availability

### Recommended rates

| Rate | Use Case |
|------|----------|
| 50 pps | Basic presence detection, minimal overhead |
| 100 pps | **Recommended** - Activity recognition (walking, sitting, gestures) |
| 600-1000 pps | Fast motion detection, precision localization |
| 0 pps | Disabled (only if you have other continuous WiFi traffic) |

### Configuration

```yaml
espectre:
  traffic_generator_rate: 100  # packets per second
```

---

## NBVI Auto-Calibration

---

ESPectre uses the **NBVI (Normalized Baseline Variability Index)** algorithm for automatic subcarrier selection.

### How it works

On first boot (or when no saved configuration exists):
1. Collects 500 CSI packets (~5 seconds)
2. Analyzes baseline characteristics of each subcarrier
3. Selects optimal 12 subcarriers based on stability and signal strength
4. Saves configuration to preferences (persists across reboots)

### Requirements during calibration

- **Room must be quiet** (no movement)
- **Wait 5-10 seconds** for completion
- Check logs for calibration status

### Manual subcarrier selection

If you prefer to specify subcarriers manually:

```yaml
espectre:
  selected_subcarriers: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
```

### Reset calibration

To trigger recalibration, you need to clear the saved preferences. This can be done by:
1. Erasing flash and re-flashing
2. Or adding a button to clear preferences programmatically

---

## Platform-Specific Configuration

---

ESPectre supports both ESP32-S3 and ESP32-C6. Choose the configuration that matches your hardware.

### ESP32-C6 (Recommended)

```yaml
esp32:
  variant: ESP32C6
  framework:
    type: esp-idf
    version: 5.4.2
    sdkconfig_options:
      CONFIG_ESP_WIFI_CSI_ENABLED: y
      CONFIG_PM_ENABLE: n
      CONFIG_ESP_WIFI_STA_DISCONNECTED_PM_ENABLE: n
      CONFIG_ESP_WIFI_AMPDU_TX_ENABLED: n
      CONFIG_ESP_WIFI_AMPDU_RX_ENABLED: y
      CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM: '16'
      CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM: '64'
      CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM: '64'
      # WiFi 6 support
      CONFIG_ESP_WIFI_11AX_SUPPORT: y
```

**Advantages**: WiFi 6 support, sufficient performance for motion detection.

### ESP32-S3

```yaml
esp32:
  variant: ESP32S3
  framework:
    type: esp-idf
    version: 5.4.2
    sdkconfig_options:
      CONFIG_ESP_WIFI_CSI_ENABLED: y
      CONFIG_PM_ENABLE: n
      CONFIG_ESP_WIFI_STA_DISCONNECTED_PM_ENABLE: n
      CONFIG_ESP_WIFI_AMPDU_TX_ENABLED: n
      CONFIG_ESP_WIFI_AMPDU_RX_ENABLED: y
      CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM: '16'
      CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM: '64'
      CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM: '64'
      # PSRAM support
      CONFIG_SPIRAM: y
      CONFIG_SPIRAM_MODE_OCT: y
```

**Advantages**: More CPU power (dual-core), for future ML features.

### Switching Platforms

To switch between platforms:

1. Change `variant` in your YAML configuration
2. Re-flash the device:

```bash
esphome run espectre.yaml
```

The ESPectre component automatically adapts to the target platform.

---

## Troubleshooting

---

### Device not discovered by Home Assistant

1. Verify WiFi credentials in `secrets.yaml`
2. Check that device and Home Assistant are on the same network
3. Look for device IP in router's DHCP client list
4. Check ESPHome logs: `esphome logs espectre.yaml`

### No motion detection

1. **Verify traffic generator is enabled** (`traffic_generator_rate > 0`)
2. Check WiFi is connected (look for IP address in logs)
3. Verify SDK configuration options are set correctly
4. Wait for NBVI calibration to complete (~5-10 seconds after boot)
5. Adjust `segmentation_threshold` (try 0.5-2.0 for more sensitivity)

### False positives (detecting motion when room is empty)

1. Increase `segmentation_threshold` (try 2.0-5.0)
2. Check for interference sources (fans, AC, moving curtains)
3. Increase `segmentation_window_size` for more stable detection

### Calibration fails

1. Ensure room is quiet during calibration (first 5-10 seconds after boot)
2. Check traffic generator is running
3. Verify WiFi connection is stable
4. Check logs for error messages

### Flash failed

**Solution:**
1. Hold BOOT button on ESP32
2. Press RESET button
3. Release BOOT button
4. Run flash command again

### View logs

```bash
# Via USB
esphome logs espectre.yaml

# Via network (after first flash)
esphome logs espectre.yaml --device espectre.local
```

---

## Tuning

---

After installation, follow the **[TUNING.md](TUNING.md)** guide to:
- Optimize detection parameters for your environment
- Understand MVS (Moving Variance Segmentation) parameters
- Configure optional filters
- Troubleshoot detection issues

---

## Getting Help

---

- 📖 **Tuning Guide**: [TUNING.md](TUNING.md)
- 📖 **Main Documentation**: [README.md](README.md)
- 🐛 **GitHub Issues**: [Report problems](https://github.com/francescopace/espectre/issues)
- 📧 **Email**: francesco.pace@gmail.com
