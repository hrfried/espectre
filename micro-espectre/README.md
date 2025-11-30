# 🛜 Micro-ESPectre 👻

**R&D Platform for Wi-Fi CSI Motion Detection - Pure Python implementation for MicroPython**

Micro-ESPectre is the **research and development platform** of the ESPectre project, designed for fast prototyping, algorithm experimentation, and academic/industrial research. It implements the core motion detection algorithms in pure Python, enabling rapid iteration without compilation overhead.

## 🎯 What is Micro-ESPectre?

Micro-ESPectre implements the ESPectre motion-detection algorithms entirely in Python and serves as the **innovation lab** where new approaches and parameters are developed and validated before being migrated to the production ESPHome component.

### 🔬 Role in the ESPectre Ecosystem

Micro-ESPectre is part of a **two-platform strategy**:

| Platform | Purpose | Target Users |
|----------|---------|--------------|
| **[ESPectre](https://github.com/francescopace/espectre)** (ESPHome) | Production deployment | Smart home users, Home Assistant |
| **Micro-ESPectre** (Python) | R&D and prototyping | Researchers, developers, academics |

**Why MQTT instead of Native API?**
Micro-ESPectre uses MQTT for maximum flexibility - it's not tied to Home Assistant and can integrate with:
- 🏭 **Industrial systems** (SCADA, PLCs, factory automation)
- 🎓 **Academic research** (data collection, algorithm validation)
- 🔧 **Custom applications** (any MQTT-compatible platform)

### 💡 Innovation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    INNOVATION CYCLE                         │
├─────────────────────────────────────────────────────────────┤
│  Micro-ESPectre (Python)          ESPectre (ESPHome)        │
│  ┌─────────────────────┐          ┌─────────────────────┐   │
│  │ • Fast prototyping  │ ──────▶  │ • Production ready  │   │
│  │ • Algorithm testing │  Port    │ • Home Assistant    │   │
│  │ • Parameter tuning  │ ──────▶  │ • Native API        │   │
│  │ • Research/academic │          │ • OTA updates       │   │
│  └─────────────────────┘          └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Benefits for R&D:**
- ⚡ **Instant deployment**: No compilation, ~5 seconds to update
- 🔧 **Easy experimentation**: Modify parameters and test immediately
- 📊 **Quick validation**: Test algorithms and configurations rapidly
- 🔄 **Proven patterns**: Validated algorithms flow to production C++ code

### What is esp32-microcsi?

[esp32-microcsi](https://github.com/francescopace/esp32-microcsi) is a MicroPython module that I wrote to expose ESP32's CSI (Channel State Information) capabilities to Python. This module makes CSI-based applications accessible to Python developers and enables rapid prototyping of WiFi sensing applications.

## 🆚 Comparison with C++ Version (ESPHome)

### Feature Comparison

| Feature | ESPHome (C++) | Python (MicroPython) | Status |
|---------|---------------|----------------------|--------|
| **Core Algorithm** |
| MVS Segmentation | ✅ | ✅ | ✅ Aligned |
| Spatial Turbulence | ✅ | ✅ | ✅ Aligned |
| Moving Variance | ✅ | ✅ | ✅ Aligned |
| **WiFi Traffic Generator** |
| Traffic Generation | ✅ | ✅ | ✅ Implemented |
| Configurable Rate | ✅ | ✅ | ✅ Implemented |
| **Configuration** |
| YAML Configuration | ✅ | ❌ | ESPHome only |
| MQTT Commands | ❌ | ✅ | Micro-ESPectre only |
| Runtime Config | ✅ (via HA) | ✅ (via MQTT) | Different methods |
| **Storage** |
| NVS Persistence | ✅ | ✅ | ✅ Implemented |
| Auto-save on config change | ✅ | ✅ | ✅ Implemented |
| Auto-load on startup | ✅ | ✅ | ✅ Implemented |
| **Automatic Subcarrier Selection** |
| NBVI Algorithm | ✅ | ✅ | ✅ Implemented |
| Percentile-based Detection | ✅ | ✅ | ✅ Implemented |
| Noise Gate | ✅ | ✅ | ✅ Implemented |
| Spectral De-correlation | ✅ | ✅ | ✅ Implemented |
| **CSI Features** |
| `features_enable` | ✅ | ❌ | Not implemented |
| 10 CSI Features | ✅ | ❌ | Not implemented |
| Feature Extraction | ✅ | ❌ | Not implemented |
| Hampel Filter | ✅ | ❌ | Not implemented |
| Savitzky-Golay Filter | ✅ | ❌ | Not implemented |
| Butterworth Filter | ✅ | ❌ | Not implemented |
| Wavelet Filter | ✅ | ❌ | Not implemented |
| **Home Assistant Integration** |
| Native API | ✅ | ❌ | ESPHome only |
| MQTT | ❌ | ✅ | Micro-ESPectre only |
| Auto-discovery | ✅ | ❌ | ESPHome only |

### Performance Comparison

| Metric | ESPHome (C++) | Python (MicroPython) |
|--------|---------------|----------------------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Memory Usage | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Deployment | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Build Time | ~15 seconds | Instant (no build) |
| Update Time | ~15 seconds (OTA) | ~5 seconds |
| HA Integration | ⭐⭐⭐⭐⭐ (Native) | ⭐⭐⭐ (MQTT) |

📊 **For detailed ESPectre performance metrics and test methodology**, see [PERFORMANCE.md](../PERFORMANCE.md) in the main repository.

### When to Use Which Version?

**Use Micro-ESPectre (Python) if you want:**
- ✅ Quick prototyping and experimentation
- ✅ Easy deployment and updates (~5 seconds)
- ✅ Core motion detection functionality
- ✅ Simple Python-based development
- ✅ MQTT-based runtime configuration
- ✅ Automatic subcarrier selection

**Use ESPectre (ESPHome) if you need:**
- ✅ Native Home Assistant integration (auto-discovery)
- ✅ Maximum performance and efficiency
- ✅ Advanced CSI feature extraction
- ✅ Multiple filtering algorithms
- ✅ Production-grade stability
- ✅ YAML-based configuration

## 📋 Requirements

### Hardware
- ESP32-S3 or ESP32-C6 board
- 2.4GHz WiFi router

### Software
- MicroPython with esp32-microcsi module installed
- MQTT broker (Home Assistant, Mosquitto, etc.)

## 🚀 Quick Start

### 1. Install MicroPython with CSI Support 

**Note:** This step is only required once to flash the patched MicroPython firmware with esp32-microcsi module to your device.

Follow the instructions at [esp32-microcsi](https://github.com/francescopace/esp32-microcsi):

```bash
# Clone esp32-microcsi repository
git clone https://github.com/francescopace/esp32-microcsi
cd esp32-microcsi

# Setup environment
./scripts/setup_env.sh

# Integrate CSI module
./scripts/integrate_csi.sh

# Build and flash (ESP32-S3)
./scripts/build_flash.sh -b ESP32_GENERIC_S3

# Or for ESP32-C6
./scripts/build_flash.sh -b ESP32_GENERIC_C6
```

### 2. Configure WiFi and MQTT

Create `config_local.py` from the template:

```bash
cp config_local.py.example config_local.py
```

Edit `config_local.py` with your credentials:

```python
# WiFi Configuration
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

# MQTT Configuration
MQTT_BROKER = "homeassistant.local"  # Your MQTT broker IP or hostname
MQTT_PORT = 1883
MQTT_USERNAME = "username"
MQTT_PASSWORD = "password"
```

**Note**: `config_local.py` overrides the defaults in `config.py`. You can also customize other settings like topic, buffer size, etc.

### 3. Upload Files to ESP32

Use the deployment script:

```bash
# Deploy only (upload files)
./deploy.sh /dev/cu.usbmodem*

# Deploy and run main application
./deploy.sh /dev/cu.usbmodem* --run

# Deploy and collect baseline data (for testing/analysis)
./deploy.sh /dev/cu.usbmodem* --collect-baseline

# Deploy and collect movement data (for testing/analysis)
./deploy.sh /dev/cu.usbmodem* --collect-movement
```

**Data Collection:**
The `--collect-baseline` and `--collect-movement` flags are used to collect CSI data samples for algorithm testing and parameter tuning. The collected binary files are automatically downloaded to the `tools/` directory and can be analyzed with the Python analysis scripts.

### 4. Run

```bash
# Run main application
mpremote connect /dev/cu.usbmodem* run src/main.py

# Or connect to REPL and run
mpremote connect /dev/cu.usbmodem*
>>> from src import main
>>> main.main()
```

## 📁 Project Structure

```
micro-espectre/
├── src/                       # Main package
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main application entry point
│   ├── config.py              # Default configuration
│   ├── segmentation.py        # MVS segmentation logic
│   ├── traffic_generator.py   # WiFi traffic generator
│   ├── nvs_storage.py         # JSON-based config persistence
│   ├── filters.py             # Signal filtering (Hampel filter)
│   ├── nbvi_calibrator.py     # NBVI automatic subcarrier selection
│   ├── data_collector.py      # CSI data collection for testing
│   └── mqtt/                  # MQTT sub-package
│       ├── __init__.py        # MQTT package initialization
│       ├── handler.py         # MQTT connection and publishing
│       └── commands.py        # MQTT command processing
├── tools/                     # Analysis and optimization tools
│   └── ...
├── config_local.py            # Local config override (gitignored)
├── config_local.py.example    # Configuration template
├── deploy.sh                  # Deployment script
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## ⚙️ Configuration

### Segmentation Parameters (config.py)

```python
SEG_WINDOW_SIZE = 50       # Moving variance window (10-200 packets)
                          # Larger = smoother, slower response
                          # Smaller = faster response, more noise

SEG_THRESHOLD = 1.0       # Motion detection threshold (0.0-10.0)
                          # Lower values = more sensitive to motion
```

### Published Data (same as ESPectre)

The system publishes JSON payloads to the configured MQTT topic (default: `home/espectre/node1`):

```json
{
  "movement": 0.0234,            // Current moving variance
  "threshold": 1.0,              // Current threshold
  "state": "idle",               // "idle" or "motion"
  "packets_processed": 42,       // Packets since last publish
  "packets_dropped": 0,          // Packets dropped since last publish
  "timestamp": 1700000000        // Unix timestamp
}
```

## 🔧 Analysis Tools

The `tools/` directory contains a comprehensive suite of Python scripts for CSI data analysis, algorithm optimization, and subcarrier selection. These tools were instrumental in developing and validating the MVS algorithm and the breakthrough **NBVI (Normalized Baseline Variability Index)** automatic subcarrier selection method.

### Quick Start

```bash
# Collect CSI data samples
./deploy.sh /dev/cu.usbmodem* --collect-baseline
./deploy.sh /dev/cu.usbmodem* --collect-movement

# Run analysis
cd tools
python 2_analyze_system_tuning.py --quick
python 11_test_nbvi_selection.py
```

### Available Tools

The tools directory includes **11 analysis scripts** covering:
- 📊 Raw data visualization and system tuning
- 🔬 MVS algorithm validation and optimization
- 🎨 I/Q constellation analysis
- 🧬 **NBVI automatic subcarrier selection** (F1=97.1%)
- 🔍 Ring geometry analysis (23+ strategies tested)
- 📈 Detection methods comparison

**For complete documentation**, see **[tools/README.md](tools/README.md)** which includes:
- Detailed description of all 11 scripts
- Usage examples and options
- NBVI algorithm explanation and results
- Performance comparisons and scientific findings

### 🧬 NBVI: Breakthrough in Automatic Subcarrier Selection

**NBVI (Normalized Baseline Variability Index)** achieves **F1=97.1%** (pure data) and **F1=91.2%** (mixed data) with **zero manual configuration** - the best automatic method tested among 23+ strategies.

**Key Results**:
- ✅ Gap to manual optimization: only **-0.2%**
- ✅ Outperforms variance-only by **+4.7%** (pure), **∞** (mixed - variance fails)
- ✅ **Percentile-based**: NO threshold configuration needed
- ✅ **Production-ready**: Validated on real CSI data

For complete NBVI documentation, algorithm details, and performance analysis, see **[tools/README.md](tools/README.md)**.

## 🧬 Automatic Subcarrier Selection (NBVI)

Micro-ESPectre implements the **NBVI (Normalized Baseline Variability Index)** algorithm for automatic subcarrier selection, achieving near-optimal performance (F1=97.1%) with **zero manual configuration**.

NBVI automatically selects the optimal 12 subcarriers from the 64 available in WiFi CSI by analyzing their stability and signal strength during a baseline period. The calibration runs automatically:
- **At first boot** (if no saved configuration exists)
- **After factory_reset** command

For complete NBVI documentation, algorithm details, performance analysis, and configuration parameters, see **[tools/README.md](tools/README.md)**.

## 🤖 Advanced Applications & Machine Learning

Micro-ESPectre is the **R&D platform** for advanced CSI-based applications requiring feature extraction and machine learning.

While [ESPectre (ESPHome)](https://github.com/francescopace/espectre) focuses on **production-ready motion detection** using mathematical algorithms (MVS + NBVI), Micro-ESPectre provides the tools and features needed for advanced applications:

- 🔬 **People counting**
- 🏃 **Activity recognition** (walking, falling, sitting, sleeping)
- 📍 **Localization and tracking**
- 👋 **Gesture recognition**

### Available Features for ML Training

Micro-ESPectre provides **10 CSI features** for machine learning applications:

**Statistical Features (5):**
- Variance
- Skewness
- Kurtosis
- Entropy
- IQR (Interquartile Range)

**Spatial Features (3):**
- Spatial Variance
- Spatial Correlation
- Spatial Gradient

**Temporal Features (2):**
- Temporal Delta Mean
- Temporal Delta Variance

### Tools & Resources

- ✅ **Analysis tools** for dataset collection (see [tools/README.md](tools/README.md))
- ✅ **Feature extraction** pipeline ready for ML training
- ✅ **MQTT-based** data streaming for real-time ML inference
- ✅ **Python-based** for rapid prototyping and experimentation

<details>
<summary>📚 Machine Learning and Deep Learning (click to expand)</summary>

The current implementation uses an **advanced mathematical approach** with 10 features and multi-criteria detection to identify movement patterns. While this provides excellent results without requiring ML training, scientific research has shown that **Machine Learning** and **Deep Learning** techniques can extract even richer information from CSI data for complex tasks like people counting, activity recognition, and gesture detection.

### Advanced Applications with ML/DL

#### 1. **People Counting**
Classification or regression models can estimate the number of people present in an environment by analyzing complex patterns in CSI.

**References:**
- *Wang et al.* (2017) - "Device-Free Crowd Counting Using WiFi Channel State Information" - IEEE INFOCOM
- *Xi et al.* (2016) - "Electronic Frog Eye: Counting Crowd Using WiFi" - IEEE INFOCOM

#### 2. **Activity Recognition**
Neural networks (CNN, LSTM, Transformer) can classify human activities like walking, falling, sitting, sleeping.

**References:**
- *Wang et al.* (2015) - "Understanding and Modeling of WiFi Signal Based Human Activity Recognition" - ACM MobiCom
- *Yousefi et al.* (2017) - "A Survey on Behavior Recognition Using WiFi Channel State Information" - IEEE Communications Magazine
- *Zhang et al.* (2019) - "WiFi-Based Indoor Robot Positioning Using Deep Neural Networks" - IEEE Access

#### 3. **Localization and Tracking**
Deep learning algorithms can estimate position and trajectory of moving people.

**References:**
- *Wang et al.* (2016) - "CSI-Based Fingerprinting for Indoor Localization: A Deep Learning Approach" - IEEE Transactions on Vehicular Technology
- *Chen et al.* (2018) - "WiFi CSI Based Passive Human Activity Recognition Using Attention Based BLSTM" - IEEE Transactions on Mobile Computing

#### 4. **Gesture Recognition**
Models trained on CSI temporal sequences can recognize hand gestures for touchless control.

**References:**
- *Abdelnasser et al.* (2015) - "WiGest: A Ubiquitous WiFi-based Gesture Recognition System" - IEEE INFOCOM
- *Jiang et al.* (2020) - "Towards Environment Independent Device Free Human Activity Recognition" - ACM MobiCom

### Available Public Datasets

- **UT-HAR**: Human Activity Recognition dataset (University of Texas)
- **Widar 3.0**: Gesture recognition dataset with CSI
- **SignFi**: Sign language recognition dataset
- **FallDeFi**: Fall detection dataset

</details>

<details>
<summary>🛜 Standardized Wi-Fi Sensing (IEEE 802.11bf) (click to expand)</summary>

Currently, only a limited number of Wi-Fi chipsets support CSI extraction, which restricts hardware options for Wi-Fi sensing applications. However, the **IEEE 802.11bf (Wi-Fi Sensing)** standard should significantly improve this situation by making CSI extraction a standardized feature.

### IEEE 802.11bf - Wi-Fi Sensing

The **802.11bf** standard was **[officially published on September 26, 2025](https://standards.ieee.org/ieee/802.11bf/11574/)**, introducing **Wi-Fi Sensing** as a native feature of the Wi-Fi protocol. Main characteristics:

🔹 **Native sensing**: Detection of movements, gestures, presence, and vital signs
🔹 **Interoperability**: Standardized support across different vendors
🔹 **Optimizations**: Specific protocols to reduce overhead and power consumption
🔹 **Privacy by design**: Privacy protection mechanisms integrated into the standard
🔹 **Greater precision**: Improvements in temporal and spatial granularity
🔹 **Existing infrastructure**: Works with already present Wi-Fi infrastructure

### Adoption Status (2025)

**Market**: The Wi-Fi Sensing market is in its early stages and is expected to experience significant growth in the coming years as the 802.11bf standard enables native sensing capabilities in consumer devices.

**Hardware availability**:
- ⚠️ **Consumer routers**: Currently **there are no widely available consumer routers** with native 802.11bf support
- 🏢 **Commercial/industrial**: Experimental devices and integrated solutions already in use
- 🔧 **Hardware requirements**: Requires multiple antennas, Wi-Fi 6/6E/7 support, and AI algorithms for signal processing

**Expected timeline**:
- **2025-2026**: First implementations in enterprise and premium smart home devices
- **2027-2028**: Diffusion in high-end consumer routers
- **2029+**: Mainstream adoption in consumer devices

### Future Benefits for Wi-Fi Sensing

When 802.11bf is widely adopted, applications like this project will become:
- **More accessible**: No need for specialized hardware or modified firmware
- **More reliable**: Standardization ensures predictable behavior
- **More efficient**: Protocols optimized for continuous sensing
- **More secure**: Privacy mechanisms integrated at the standard level
- **More powerful**: Ability to detect even vital signs (breathing, heartbeat)

**Perspective**: In the next 3-5 years, routers and consumer devices will natively support Wi-Fi Sensing, making projects like this implementable without specialized hardware or firmware modifications. This will open new possibilities for smart home, elderly care, home security, health monitoring, and advanced IoT applications.

**For now**: Solutions like this project based on **ESP32 CSI API** remain the most accessible and economical way to experiment with Wi-Fi Sensing.

</details>

---

## 🖥️ Interactive CLI

Micro-ESPectre includes an interactive command-line interface (`espectre-cli.py`) for easy device control and monitoring via MQTT.

### Installation

```bash
# From the project root directory
pip install -r requirements.txt
```

### Usage

```bash
cd micro-espectre

# Connect to default broker (homeassistant.local)
python espectre-cli.py

# Connect to specific broker
python espectre-cli.py --broker 192.168.1.100 --port 1883

# With authentication
python espectre-cli.py --broker homeassistant.local --username mqtt --password mqtt
```

### Features

- **Interactive prompt** with autocompletion (TAB) and history search (Ctrl+R)
- **All MQTT commands** available (see table below)
- **Web UI launcher**: `webui` command opens `espectre-monitor.html` in browser
- **YAML-formatted responses** for easy reading
- **Environment variables** support via `.env` file

### CLI-Only Commands

| Command | Description |
|---------|-------------|
| `webui` | Open web monitor in browser |
| `clear` | Clear screen |
| `help` | Show all commands |
| `about` | Show about information |
| `exit` | Exit CLI |

### Web Tools

Two HTML-based tools are included for visualization:

- **`espectre-monitor.html`**: Real-time motion monitoring dashboard with charts
- **`espectre-theremin.html`**: Audio sonification of CSI data (experimental)

---

## 📡 MQTT Integration

Micro-ESPectre uses MQTT for communication with Home Assistant and runtime configuration.

> **Note**: The main ESPectre component (ESPHome) uses **Native API** instead of MQTT for Home Assistant integration. Micro-ESPectre retains MQTT support for flexibility and compatibility with non-Home Assistant setups.

### Available MQTT Commands

Publish commands to `home/espectre/node1/cmd`:

| Command | Example | Description |
|---------|---------|-------------|
| `info` | `info` | Get system information |
| `stats` | `stats` | Get runtime statistics |
| `segmentation_threshold` | `segmentation_threshold 1.5` | Set detection threshold |
| `segmentation_window_size` | `segmentation_window_size 100` | Set window size |
| `subcarrier_selection` | `subcarrier_selection 11,12,13,...` | Set subcarriers |
| `traffic_generator_rate` | `traffic_generator_rate 100` | Set packet rate |
| `smart_publishing` | `smart_publishing on` | Enable/disable smart publishing |
| `factory_reset` | `factory_reset` | Reset to defaults |

### Configuration Persistence

All configuration changes made via MQTT commands are **automatically saved** to a JSON file (`espectre_config.json`) on the ESP32 filesystem and **automatically loaded** on startup, ensuring settings persist across reboots.

## 🏠 Home Assistant Integration

Micro-ESPectre integrates with Home Assistant via MQTT. Add these sensors to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "ESPectre Movement"
      state_topic: "home/espectre/node1"
      value_template: "{{ value_json.movement }}"
      unit_of_measurement: ""
      
    - name: "ESPectre State"
      state_topic: "home/espectre/node1"
      value_template: "{{ value_json.state }}"

  binary_sensor:
    - name: "ESPectre Motion"
      state_topic: "home/espectre/node1"
      value_template: "{{ value_json.state }}"
      payload_on: "motion"
      payload_off: "idle"
      device_class: motion
```

> **Tip**: For seamless Home Assistant integration with auto-discovery, consider using the main [ESPectre ESPHome component](https://github.com/francescopace/espectre) instead.

## 📚 Scientific References

This section contains extensive research references in Wi-Fi sensing and CSI-based movement detection. These academic works and theses provide valuable insights into mathematical signal processing approaches and machine learning techniques for human activity recognition using Wi-Fi Channel State Information.

### University Theses

1. **Wi-Fi Sensing per Human Identification attraverso CSI**  
   University thesis (in Italian) covering CSI data collection for human recognition through Wi-Fi signal analysis, with in-depth exploration of mathematical signal processing methods.  
   📄 [Read thesis](https://amslaurea.unibo.it/id/eprint/29166/1/tesi.pdf)

2. **Channel State Information (CSI) Features Collection in Wi-Fi**  
   Detailed analysis of CSI feature collection and processing in Wi-Fi environments, with methods for extraction and analysis suitable for mathematical processing.  
   📄 [Read thesis](https://www.politesi.polimi.it/handle/10589/196727)

3. **Wi-Fi CSI for Human Activity Recognition** - UBC  
   Baseline detection and calibration-free approaches for activity recognition.  
   📄 [Read thesis](https://open.library.ubc.ca/media/stream/pdf/24/1.0365967/4)

### Scientific Papers

4. **Indoor Motion Detection Using Wi-Fi Channel State Information (2018)**  
   Scientific article describing indoor movement detection using CSI with approaches based on signal mathematics and physics. False positive reduction and sensitivity optimization.  
   📄 [Read paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6068568/)

5. **WiFi Motion Detection: A Study into Efficacy and Performance (2019)**  
   Study using CSI data collected from standard devices to detect movements, with analysis of signal processing methods to extract movement events without relying on ML.  
   📄 [Read paper](https://arxiv.org/abs/1908.08476)

6. **CSI-HC: A WiFi-Based Indoor Complex Human Motion Recognition Using Channel State Information (2020)**  
   Recognition of complex indoor movements through CSI with methods based on mathematical signal features, ideal for projects with signal-based analysis without advanced ML.  
   📄 [Read paper](https://onlinelibrary.wiley.com/doi/10.1155/2020/3185416)

7. **Location Intelligence System for People Estimation in Indoor Environment During Emergency Operation (2022)**  
   Demonstrates the use of ESP32 with wavelet filtering (Daubechies db4) for people detection in emergency scenarios. This paper directly influenced ESPectre's wavelet filter implementation.  
   📄 [Read paper](https://scholarspace.manoa.hawaii.edu/server/api/core/bitstreams/a2d2de7c-7697-485b-97c5-62f4bf1260d0/content)

8. **Mitigation of CSI Temporal Phase Rotation** - PMC  
   B2B calibration methods for phase analysis in CSI-based sensing.  
   📄 [Read paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6263436/)

9. **CSI-based Passive Intrusion Detection** - NIH  
   Multipath components and subcarrier sensitivity analysis for intrusion detection.  
   📄 [Read paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11630712/)

10. **Time-Selective RNN for Multi-Room Detection** - arXiv  
    Environment-dependent channel optimization for multi-room scenarios.  
    📄 [Read paper](https://arxiv.org/html/2304.13107v2)

11. **CIRSense: Rethinking WiFi Sensing** - arXiv  
    SSNR (Sensing Signal-to-Noise Ratio) optimization for sensing applications.  
    📄 [Read paper](https://arxiv.org/html/2510.11374v1)

12. **MVS Segmentation** - ResearchGate  
    Moving Variance Segmentation algorithm: the fused CSI stream and corresponding moving variance sequence.  
    📄 [Read paper](https://www.researchgate.net/figure/MVS-segmentation-a-the-fused-CSI-stream-b-corresponding-moving-variance-sequence_fig6_326244454)

13. **CSI-F: Feature Fusion Method** - MDPI  
    Hampel filter and statistical robustness for CSI feature extraction.  
    📄 [Read paper](https://www.mdpi.com/1424-8220/24/3/862)

14. **Linear-Complexity Subcarrier Selection** - ResearchGate  
    Computational efficiency strategies for embedded systems.  
    📄 [Read paper](https://www.researchgate.net/publication/397240630)

15. **Passive Indoor Localization** - PMC  
    SNR considerations and noise gate strategies for indoor localization.  
    📄 [Read paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6412876/)

16. **Subcarrier Selection for Indoor Localization** - ResearchGate  
    Spectral de-correlation and feature diversity for optimal subcarrier selection.  
    📄 [Read paper](https://www.researchgate.net/publication/326195991)

These references demonstrate that effective Wi-Fi sensing can be achieved through both mathematical and machine learning approaches, supporting Micro-ESPectre's role as the R&D platform for algorithm development and validation.

## Related Projects

- [ESPectre (ESPHome)](https://github.com/francescopace/espectre) - Main project with native Home Assistant integration
- [esp32-microcsi](https://github.com/francescopace/esp32-microcsi) - MicroPython CSI module
- [MicroPython](https://micropython.org/)

## 📄 License

GPLv3 - See ESPEctre LICENSE file for details

## 👤 Author

**Francesco Pace**  
📧 Email: francesco.pace@gmail.com  
💼 LinkedIn: [linkedin.com/in/francescopace](https://www.linkedin.com/in/francescopace/)
