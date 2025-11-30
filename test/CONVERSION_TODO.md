# Test Conversion TODO

Questa è una guida per completare la conversione dei test rimanenti da ESP-IDF a PlatformIO.

## ✅ Completato

- [x] Struttura base PlatformIO
- [x] `platformio.ini` configurato
- [x] `src/main.cpp` creato
- [x] Symlink `lib/espectre` → `components/espectre`
- [x] Dati CSI spostati in `data/`
- [x] README aggiornato
- [x] `test_filters` convertito come esempio (poi rimosso - filtri non più presenti)
- [x] `test_segmentation` convertito (5 test core del processore CSI)

## ❌ Test Rimossi (Funzionalità Non Più Presenti)

Le seguenti funzionalità sono state rimosse durante il porting a ESPHome:

### test_filters.c
- **Rimosso**: Butterworth, Hampel, Savitzky-Golay filters
- **Motivo**: Filtri rimossi dal componente ESPHome

### test_wavelet.c
- **Rimosso**: Wavelet denoising
- **Motivo**: Wavelet processing rimosso dal componente ESPHome

### test_features.c
- **Rimosso**: Feature extraction (variance, skewness, kurtosis, entropy, ecc.)
- **Motivo**: Feature extraction rimossa dal componente ESPHome

### test_pca_subcarrier.c
- **Rimosso**: PCA subcarrier analysis
- **Motivo**: PCA analysis rimossa dal componente ESPHome

### test_performance_suite.c
- **Rimosso**: Performance suite con feature ranking
- **Motivo**: Dipendeva da feature extraction che è stata rimossa

## 📊 Test Finali

**Test Attivi**: 1 suite
- `test_segmentation` - 5 test per il processore CSI core

**Test Rimossi**: 5 suite (funzionalità non più presenti nel porting ESPHome)

## ⚠️ Stato Compilazione

**PROBLEMA**: I test non compilano attualmente perché `components/espectre` contiene dipendenze ESPHome (`esphome/core/component.h`, `esphome/core/log.h`, ecc.) che non sono disponibili in un progetto PlatformIO standalone.

**SOLUZIONE NECESSARIA**: 
Per rendere i test funzionanti, è necessario:
1. Separare il codice core CSI (csi_processor, calibration_manager) dalle dipendenze ESPHome
2. Creare una versione "standalone" dei file core senza include ESPHome
3. Oppure creare mock/stub per gli header ESPHome necessari

**ALTERNATIVA**: 
Mantenere i test come documentazione della struttura, ma eseguirli solo quando il componente è integrato in un progetto ESPHome completo.

**File con dipendenze ESPHome**:
- `espectre_component.h/cpp` - dipende da `esphome/core/component.h`
- `config_manager.h/cpp` - dipende da `esphome/core/preferences.h`
- `sensor_publisher.h/cpp` - dipende da `esphome/components/sensor/sensor.h`
- `utils.h` - dipende da `esphome/core/log.h`
- `csi_manager.cpp` - dipende da `esphome/core/log.h`

## 🔧 Template di Conversione

Per ogni test, seguire questo template:

```cpp
/*
 * ESPectre - [Nome Test] Unit Tests
 * 
 * [Descrizione]
 * 
 * Author: Francesco Pace <francesco.pace@gmail.com>
 * License: GPLv3
 */

#include <unity.h>
#include <math.h>
#include <string.h>

// Include headers from lib/espectre
extern "C" {
    // #include "header_necessari.h"
}

void setUp(void) {
    // Setup before each test
}

void tearDown(void) {
    // Cleanup after each test
}

// Test functions
void test_nome_test(void) {
    // Codice test (copiato da .c originale)
    TEST_ASSERT_EQUAL(expected, actual);
}

void process(void) {
    UNITY_BEGIN();
    RUN_TEST(test_nome_test);
    // ... altri test
    UNITY_END();
}

#ifdef ARDUINO
void setup() {
    delay(2000);
    process();
}

void loop() {
    // Empty
}
#else
int main(int argc, char **argv) {
    return process();
}
#endif
```

## 📝 Passi per Conversione

Per ogni test:

1. **Crea directory**: `mkdir -p test/test_[nome]`
2. **Crea file**: `test/test_[nome]/test_[nome].cpp`
3. **Copia contenuto** dal file `.c` originale
4. **Converti macro**:
   - `TEST_CASE_ESP(name, "[tag]")` → `void test_name(void)`
5. **Aggiungi boilerplate**:
   - `setUp()` e `tearDown()`
   - `process()` con `UNITY_BEGIN()` e `UNITY_END()`
   - `main()` / `setup()` / `loop()`
6. **Aggiungi includes** necessari
7. **Testa**: `pio test -f test_[nome]`

## 🎯 Priorità

1. **Alta**: `test_performance` (test core)
2. **Media**: `test_segmentation`, `test_wavelet`
3. **Bassa**: `test_features`, `test_pca`

## 🔍 Note Importanti

### Headers da Includere

I file header sono disponibili tramite symlink `lib/espectre/`:
- `csi_processor.h`
- `calibration_manager.h`
- `config_manager.h`
- `utils.h`
- ecc.

### Dati CSI Reali

I dati CSI sono in `data/`:
- `real_csi_arrays.inc`
- `real_csi_data_esp32.h`

Includere con: `#include "real_csi_data_esp32.h"`

### Differenze C vs C++

- File `.c` → `.cpp`
- Wrappare C headers con `extern "C" { }`
- Usare `nullptr` invece di `NULL` (opzionale)

## ✅ Testing

Dopo ogni conversione:

```bash
# Test singolo
pio test -f test_[nome] -v

# Tutti i test
pio test

# Con output per analisi
pio test | tee test_output.log
```

## 📚 Riferimenti

- Template esempio: `test/test_filters/test_filters.cpp`
- Documentazione PlatformIO: https://docs.platformio.org/en/latest/plus/unit-testing.html
- Unity assertions: https://github.com/ThrowTheSwitch/Unity/blob/master/docs/UnityAssertionsReference.md
