# 🛜 ESPectre 👻 - Test Suite

Test suite based on **PlatformIO Unity** to validate ESPectre CSI algorithms.

## 🎯 Overview

The test suite has been converted from ESP-IDF to PlatformIO for:
- ✅ Integration with ESPHome environment (same virtualenv)
- ✅ Simplified setup (no separate ESP-IDF installation)
- ✅ Single command to run tests (`pio test`)
- ✅ Better integration with VSCode and CI/CD

**Total Tests**: 24
- **Performance Tests (CORE)**: 2
- **Feature Extraction & Tuning**: 3 (real data only)
- **Segmentation**: 5
- **Filters**: 5
- **Wavelet**: 9

---

## 🚀 Quick Start

### Prerequisites

**PlatformIO** is a professional embedded development platform that simplifies building and testing firmware for microcontrollers. The `pio` command-line tool is already installed in the ESPHome virtualenv:

```bash
# Activate ESPHome virtualenv
source ../venv/bin/activate  # On macOS/Linux
# ..\venv\Scripts\activate   # On Windows

# Verify PlatformIO
pio --version
```

### Build and Run Tests

Tests can be executed in two modes:

1. **Local (Native)** - Tests run on your computer using mocked ESP-IDF libraries for fast iteration
2. **On Device** - Tests run on actual ESP32 hardware for real-world validation

**Note**: ESP-IDF functions (e.g., `ESP_LOGI`, `esp_get_free_heap_size`) have been mocked in `lib/esp_mocks/` to enable local testing without hardware. See [ESP-IDF Mocks](#-espidf-mocks) section for details.

```bash
cd test

# Run all tests LOCALLY (native, no hardware needed)
pio test -e native

# Run tests ON DEVICE (requires ESP32 connected via USB)
pio test -e esp32dev

# Run specific tests locally
pio test -e native -f test_segmentation

# Run specific tests on device
pio test -e esp32dev -f test_segmentation

# With verbose output
pio test -e native -v

# On specific USB port (for device testing)
pio test -e esp32dev --upload-port /dev/ttyUSB0

# List available tests without running them
pio test -e native --list-tests
```

---

## 📁 Test Suite Structure

### Directory Structure

```
test/
├── platformio.ini              # PlatformIO configuration
├── src/
│   └── main.cpp               # Dummy main (tests in test/)
├── test/                       # PlatformIO Unity tests
│   ├── test_filters/
│   │   └── test_filters.cpp
│   ├── test_segmentation/
│   │   └── test_segmentation.cpp
│   ├── test_wavelet/
│   │   └── test_wavelet.cpp
│   └── test_performance/
│       └── test_performance.cpp
├── lib/
│   └── esp_mocks/             # ESP-IDF mocks for native testing
│       ├── esp_err.h
│       ├── ...
│       └── sdkconfig.h
└── data/                       # Real CSI data
    ├── real_csi_arrays.inc
    └── real_csi_data_esp32.h
```

### 📊 Performance Tests (CORE) - 2 tests

Primary tests for validating Home Assistant integration:

#### 1. `performance_suite_comprehensive`
- Evaluates all 10 features individually
- Calculates: Accuracy, Precision, **Recall**, F1-Score, FP/FN rates
- Ranks features by recall (priority for security)
- Generates confusion matrix
- **Output**: JSON with best feature and metrics

#### 2. `threshold_optimization_for_recall`
- Generates 50-point ROC curve
- Calculates AUC (Area Under Curve)
- Finds optimal threshold for 90% recall target
- Trade-off analysis (80%, 85%, 90%, 95%, 99% recall)
- **Output**: JSON with ROC data and optimal threshold

### 🎯 Feature Extraction & Segmentation Tuning - 3 tests

- `features_differ_between_baseline_and_movement` - Feature separation validation
- `segmentation_threshold_tuning_with_real_csi` - Segmentation threshold tuning
- `pca_subcarrier_analysis_on_real_data` - PCA subcarrier optimization

### 📈 Segmentation - 5 tests

Temporal event segmentation for activity recognition:
- `test_segmentation_init` - Initialization and default values
- `test_segmentation_parameters` - Parameter setters/getters and validation
- `test_segmentation_reset` - Reset functionality and state preservation
- `test_segmentation_handles_invalid_input` - Input validation and error handling
- `test_segmentation_stress_test` - Stress testing with large datasets

### 🔧 Filters - 5 tests

Signal filtering and preprocessing tests:
- `butterworth_filter_initialization`
- `filter_buffer_operations`
- `hampel_filter_removes_outliers`
- `filter_pipeline_with_wavelet_integration`
- `filter_pipeline_with_wavelet_disabled`

### 🌊 Wavelet - 9 tests

Wavelet denoising and signal processing tests:
- `wavelet_filter_initialization`
- `wavelet_soft_thresholding`
- `wavelet_hard_thresholding`
- `wavelet_denoising_reduces_noise`
- `wavelet_streaming_mode`
- `wavelet_handles_invalid_parameters`
- `wavelet_level_clamping`
- `wavelet_db4_coefficients_sum_correctly`
- `wavelet_preserves_dc_component`

---

## 🔧 ESP-IDF Mocks

The test suite includes comprehensive mocks for ESP-IDF APIs to enable native (local) testing without hardware. These mocks are located in `lib/esp_mocks/`:

### Core ESP-IDF Mocks
- **`esp_err.h`** - Error codes and return types
- **`esp_log.h`** - Logging macros (`ESP_LOGI`, `ESP_LOGE`, etc.)
- **`esp_system.h`** - System functions (`esp_get_free_heap_size`, etc.)
- **`esp_timer.h`** - Timer functions (`esp_timer_get_time`, etc.)

### WiFi & Network Mocks
- **`esp_wifi.h`** - WiFi API (`esp_wifi_set_mode`, `esp_wifi_get_ps`, `esp_wifi_get_bandwidth`, CSI configuration)
- **`esp_event.h`** - Event loop and event handling
- **`esp_netif.h`** - Network interface management
- **`lwip/sockets.h`** - Socket API (uses system sockets on native)
- **`lwip/inet.h`** - Network address conversion macros

### FreeRTOS Mocks
- **`freertos/FreeRTOS.h`** - FreeRTOS types and constants
- **`freertos/task.h`** - Task management (`xTaskCreate`, `vTaskDelete`, `eTaskGetState`, etc.)

### Configuration
- **`sdkconfig.h`** - SDK configuration defines

All mocks are designed to:
- ✅ Return safe default values for testing
- ✅ Avoid actual hardware/system calls
- ✅ Support both C and C++ code
- ✅ Match ESP-IDF API signatures

---

## 🔧 PlatformIO Configuration

The `platformio.ini` file configures:

- **Platform**: ESP32 (espressif32)
- **Framework**: ESP-IDF
- **Test Framework**: Unity
- **Library Directories**: `lib_extra_dirs = ../components` - Includes ESPectre component source files
- **Build Flags**: Include paths (`-I ../components/espectre`), Unity double precision
- **Monitor**: 115200 baud, exception decoder, colorize

**Note**: The ESPectre component source files are included directly from `../components/espectre` using `lib_extra_dirs` and include paths. No symlink is required.

---

## 📊 Interpreting Results

### Performance Suite

**Key Metrics:**
- **Recall**: Percentage of movements detected (target: ≥90%)
- **FP Rate**: False positive rate (target: ≤10%)
- **F1-Score**: Harmonic mean of precision and recall

**Example Output:**
```
Rank  Feature                   Recall    FN Rate   FP Rate   F1-Score
────────────────────────────────────────────────────────────────────────
✅  1  temporal_delta_mean      63.13%    36.87%    32.53%    61.46%
✅  2  spatial_gradient         63.18%    36.82%    21.72%    56.63%
⚠️   3  entropy                  59.70%    40.30%    67.98%    52.44%
```

---

## 🔍 Troubleshooting

### Build Errors

**Common Issues:**
1. **Missing mock files**: Ensure all ESP-IDF mocks are present in `lib/esp_mocks/`
2. **Include path errors**: Check that `platformio.ini` includes `-I lib/esp_mocks` for native environment
3. **Function signature mismatches**: Update mocks if ESP-IDF API changes

**Solutions:**
- Run `pio test -e native -vvv` for verbose build output
- Verify all required mock headers exist
- Check that mock function signatures match ESP-IDF APIs

### Test Failures

**Segmentation Tests:**
- `test_segmentation_parameters` fails: Check that `csi_processor_init()` validates window_size (10-200 range)
- Window size validation: Ensure invalid values (0, <10, >200) cause init to return `false`

### Low Recall (<90%)

**Solutions:**
1. Run `threshold_optimization_for_recall` to find optimal threshold
2. Check `performance_suite_comprehensive` for best features
3. Consider combining multiple features
4. Adjust debouncing (reduce from 3 to 2)

### High False Positive Rate (>10%)

**Solutions:**
1. Increase threshold slightly
2. Enable Hampel filter (outlier removal)
3. Increase debouncing (from 3 to 5)

### Unstable State Transitions (>6)

**Solutions:**
1. Increase debouncing count
2. Increase persistence timeout
3. Add hysteresis (dual thresholds)

---

## 🎓 Best Practices

1. **Always Run Performance Tests First** - Start with `performance_suite_comprehensive`
2. **Optimize Threshold** - Use `threshold_optimization_for_recall`
3. **Analyze with Python** - Generate visualizations for better insights


---

## 📦 Real CSI Data

The `data/` directory contains real CSI packets:
- 1000 baseline packets (empty room)
- 1000 movement packets (person walking)

These are used for realistic detection testing with real CSI data.

---

## ➕ Adding New Tests

### 1. Create Test File

Create `test/test_my_feature/test_my_feature.cpp`:

```cpp
#include <unity.h>

void setUp(void) {}
void tearDown(void) {}

void test_my_new_feature(void) {
    TEST_ASSERT_EQUAL(expected, actual);
}

void process(void) {
    UNITY_BEGIN();
    RUN_TEST(test_my_new_feature);
    UNITY_END();
}

#ifdef ARDUINO
void setup() { delay(2000); process(); }
void loop() {}
#else
int main(int argc, char **argv) { return process(); }
#endif
```

### 2. Run Test

```bash
pio test -f test_my_feature
```

---

## 🔄 Migration from ESP-IDF

This test suite has been converted from ESP-IDF to PlatformIO to simplify usage.

**Main differences:**

| ESP-IDF | PlatformIO |
|---------|------------|
| `idf.py build flash monitor` | `pio test` |
| Requires ESP-IDF installed | Uses PlatformIO (already in virtualenv) |
| `TEST_CASE_ESP(name, "[tag]")` | `void test_name(void)` + `RUN_TEST()` |
| `test_app_main.c` | `test/test_*/test_*.cpp` |

---

## 🆘 Support

For issues or questions:
- Open an issue on GitHub: https://github.com/francescopace/espectre/issues
- Email: francesco.pace@gmail.com

---

## 🎉 PlatformIO Benefits

1. ✅ **Same ESPHome environment** - No additional setup
2. ✅ **Simple command** - `pio test` instead of `idf.py build flash monitor`
3. ✅ **VSCode integration** - Native debugging, IntelliSense
4. ✅ **Easy CI/CD** - Single command for GitHub Actions
5. ✅ **Cross-platform** - Works on Windows/Mac/Linux
