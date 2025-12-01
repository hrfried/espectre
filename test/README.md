# ESPectre Test Suite

Test suite basata su **PlatformIO Unity** per validare algoritmi CSI di ESPectre.

## 🎯 Overview

La test suite è stata convertita da ESP-IDF a PlatformIO per:
- ✅ Integrazione con l'ambiente ESPHome (stesso virtualenv)
- ✅ Setup semplificato (nessuna installazione ESP-IDF separata)
- ✅ Comando unico per eseguire test (`pio test`)
- ✅ Migliore integrazione con VSCode e CI/CD

**Total Tests**: 25
- **Performance Tests (CORE)**: 2
- **Feature Extraction & Tuning**: 3 (real data only)
- **Segmentation**: 6
- **Filters**: 5
- **Wavelet**: 9

---

## 🚀 Quick Start

### Prerequisites

PlatformIO è già installato nel virtualenv ESPHome:

```bash
# Attiva virtualenv ESPHome
source ../venv/bin/activate  # On macOS/Linux
# ..\venv\Scripts\activate   # On Windows

# Verifica PlatformIO
pio --version
```

### Build and Run Tests

```bash
cd test

# Esegui tutti i test
pio test

# Esegui test specifici
pio test -f test_filters
pio test -f test_performance

# Con output verboso
pio test -v

# Su porta specifica
pio test --upload-port /dev/ttyUSB0
```

### Capture Test Output for Analysis

```bash
cd test
pio test | tee test_output.log
```

### Analyze Results with Python

```bash
cd test
pip install -r requirements.txt  # Se non già fatto
python analyze_test_results.py test_output.log
open test_results/report.html
```

---

## 📁 Test Suite Structure

### Struttura Directory

```
test/
├── platformio.ini              # Configurazione PlatformIO
├── src/
│   └── main.cpp               # Main dummy (test in test/)
├── test/                       # Test PlatformIO Unity
│   ├── test_filters/
│   │   └── test_filters.cpp
│   ├── test_segmentation/
│   │   └── test_segmentation.cpp
│   ├── test_wavelet/
│   │   └── test_wavelet.cpp
│   └── test_performance/
│       └── test_performance.cpp
├── lib/
│   └── espectre/              # Symlink a components/espectre
├── data/                       # Dati CSI reali
│   ├── real_csi_arrays.inc
│   └── real_csi_data_esp32.h
└── analyze_test_results.py    # Analisi risultati
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

### 📈 Segmentation - 6 tests

Temporal event segmentation for activity recognition:
- `segmentation_init`
- `spatial_turbulence_calculation`
- `segmentation_parameters`
- `segmentation_no_false_positives`
- `segmentation_movement_detection`
- `segmentation_reset`

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

## 🔧 PlatformIO Configuration

Il file `platformio.ini` configura:

- **Platform**: ESP32 (espressif32)
- **Framework**: ESP-IDF
- **Test Framework**: Unity
- **Build Flags**: Include paths, Unity double precision
- **Monitor**: 115200 baud, exception decoder, colorize

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

## 🐍 Python Analysis Tools

The `analyze_test_results.py` script generates:
- `test_results/roc_curve.png` - ROC curve
- `test_results/precision_recall_curve.png` - Precision-Recall curve
- `test_results/confusion_matrix.png` - Confusion matrix heatmap
- `test_results/temporal_scenarios.png` - Scenario comparison
- `test_results/home_assistant_summary.png` - Integration assessment
- `test_results/report.html` - **Comprehensive HTML report**

---

## 🔍 Troubleshooting

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

## 📝 Example Workflow

```bash
# 1. Attiva virtualenv
source ../venv/bin/activate  # On macOS/Linux
# ..\venv\Scripts\activate   # On Windows

# 2. Build e run tests
cd test
pio test | tee test_output.log

# 3. Analyze results
python analyze_test_results.py test_output.log

# 4. View report
open test_results/report.html  # macOS
# or xdg-open test_results/report.html  # Linux
# or start test_results/report.html  # Windows

# 5. Adjust configuration based on recommendations
# Edit components/espectre/*.cpp or use MQTT commands

# 6. Re-run tests to validate improvements
pio test
```

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

## 🔄 Migrazione da ESP-IDF

Questa test suite è stata convertita da ESP-IDF a PlatformIO per semplificare l'uso.

**Differenze principali:**

| ESP-IDF | PlatformIO |
|---------|------------|
| `idf.py build flash monitor` | `pio test` |
| Richiede ESP-IDF installato | Usa PlatformIO (già in virtualenv) |
| `TEST_CASE_ESP(name, "[tag]")` | `void test_name(void)` + `RUN_TEST()` |
| `test_app_main.c` | `test/test_*/test_*.cpp` |

---

## 🆘 Support

For issues or questions:
- Open an issue on GitHub: https://github.com/francescopace/espectre/issues
- Email: francesco.pace@gmail.com

---

## 🎉 Vantaggi PlatformIO

1. ✅ **Stesso ambiente ESPHome** - Nessun setup aggiuntivo
2. ✅ **Comando semplice** - `pio test` invece di `idf.py build flash monitor`
3. ✅ **Integrazione VSCode** - Debugging, IntelliSense nativo
4. ✅ **CI/CD facile** - Un solo comando per GitHub Actions
5. ✅ **Cross-platform** - Funziona su Windows/Mac/Linux
