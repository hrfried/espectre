/*
 * ESPectre - Filter Manager
 * 
 * Manages signal filtering pipeline for CSI data.
 * Provides Butterworth, Wavelet, Hampel, and Savitzky-Golay filters.
 * 
 * Author: Francesco Pace <francesco.pace@gmail.com>
 * License: GPLv3
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include "wavelet.h"

namespace esphome {
namespace espectre {

// Filter design constants
constexpr int BUTTERWORTH_ORDER = 4;
constexpr float BUTTERWORTH_CUTOFF = 8.0f;  // Hz
constexpr int SAVGOL_WINDOW_SIZE = 5;       // must be odd
constexpr float MAD_SCALE_FACTOR = 1.4826f; // Median Absolute Deviation scale factor

// Hampel filter for turbulence (MVS preprocessing)
constexpr bool ENABLE_HAMPEL_TURBULENCE_FILTER = true;
constexpr int HAMPEL_TURBULENCE_WINDOW = 7;
constexpr float HAMPEL_TURBULENCE_THRESHOLD = 4.0f;

// Hampel turbulence filter state (for MVS preprocessing)
struct hampel_turbulence_state_t {
    float buffer[HAMPEL_TURBULENCE_WINDOW];
    uint8_t index;
    uint8_t count;
};

// Butterworth filter state
struct butterworth_filter_t {
    float b[BUTTERWORTH_ORDER + 1];  // numerator coefficients
    float a[BUTTERWORTH_ORDER + 1];  // denominator coefficients
    float x[BUTTERWORTH_ORDER + 1];  // input history
    float y[BUTTERWORTH_ORDER + 1];  // output history
    bool initialized;
};

// Filter buffer for windowed operations
struct filter_buffer_t {
    float data[SAVGOL_WINDOW_SIZE];
    size_t index;
    size_t count;
};

// Filter configuration
struct filter_config_t {
    bool butterworth_enabled;
    bool wavelet_enabled;           // Wavelet denoising (optional, high cost)
    int wavelet_level;              // Decomposition level (1-3)
    float wavelet_threshold;        // Noise threshold
    bool hampel_enabled;
    float hampel_threshold;
    bool savgol_enabled;
};

/**
 * Filter Manager
 * 
 * Manages the complete signal filtering pipeline for CSI data.
 * Handles initialization and application of all filters.
 */
class FilterManager {
 public:
  /**
   * Initialize all filters
   * 
   * @param wavelet_level Wavelet decomposition level (1-3)
   * @param wavelet_threshold Wavelet noise threshold
   */
  void init(uint8_t wavelet_level, float wavelet_threshold);
  
  /**
   * Apply the complete filter pipeline to a raw value
   * 
   * @param raw_value Input sample
   * @param config Filter configuration (which filters are enabled)
   * @return Filtered value
   */
  float apply(float raw_value, const filter_config_t* config);
  
  /**
   * Get pointer to butterworth filter (for external access if needed)
   */
  butterworth_filter_t* get_butterworth() { return &butterworth_; }
  
  /**
   * Get pointer to wavelet state (for external access if needed)
   */
  wavelet_state_t* get_wavelet() { return &wavelet_; }
  
  /**
   * Get pointer to filter buffer (for external access if needed)
   */
  filter_buffer_t* get_filter_buffer() { return &filter_buffer_; }
  
  // Static filter functions (can be used independently)
  
  /**
   * Initialize Butterworth low-pass filter
   */
  static void butterworth_init(butterworth_filter_t *filter);
  
  /**
   * Apply Butterworth IIR filter
   */
  static float butterworth_filter(butterworth_filter_t *filter, float input);
  
  /**
   * Apply Hampel filter for outlier detection
   */
  static float hampel_filter(const float *window, size_t window_size, 
                             float current_value, float threshold);
  
  /**
   * Apply Hampel filter to turbulence value (for MVS preprocessing)
   */
  static float hampel_filter_turbulence(hampel_turbulence_state_t *state, float turbulence);
  
  /**
   * Initialize Hampel turbulence filter state
   */
  static void hampel_turbulence_init(hampel_turbulence_state_t *state);
  
  /**
   * Apply Savitzky-Golay filter
   */
  static float savitzky_golay_filter(const float *window, size_t window_size);
  
  /**
   * Initialize filter buffer
   */
  static void filter_buffer_init(filter_buffer_t *fb);
  
  /**
   * Add sample to filter buffer
   */
  static void filter_buffer_add(filter_buffer_t *fb, float value);
  
  /**
   * Get window of samples from filter buffer
   */
  static void filter_buffer_get_window(const filter_buffer_t *fb, float *window, 
                                       size_t window_capacity, size_t *size);
  
  /**
   * Apply complete filter pipeline
   */
  static float apply_filter_pipeline(float raw_value, 
                                     const filter_config_t *config,
                                     butterworth_filter_t *butterworth,
                                     wavelet_state_t *wavelet,
                                     filter_buffer_t *buffer);
  
 private:
  butterworth_filter_t butterworth_{};
  filter_buffer_t filter_buffer_{};
  wavelet_state_t wavelet_{};
};

}  // namespace espectre
}  // namespace esphome
