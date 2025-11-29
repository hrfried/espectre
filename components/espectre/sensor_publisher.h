/*
 * ESPectre - Sensor Publisher
 * 
 * Centralizes ESPHome sensor publishing logic.
 * Reduces code duplication and improves maintainability.
 * 
 * Author: Francesco Pace <francesco.pace@gmail.com>
 * License: GPLv3
 */

#pragma once

#include "esphome/components/sensor/sensor.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "csi_processor.h"
#include "csi_features.h"

namespace esphome {
namespace espectre {

/**
 * Sensor Publisher
 * 
 * Manages publishing of all ESPectre sensors to ESPHome.
 * Handles both motion sensors and feature sensors.
 */
class SensorPublisher {
 public:
  // Motion sensors
  void set_movement_sensor(sensor::Sensor *sensor) { movement_sensor_ = sensor; }
  void set_threshold_sensor(sensor::Sensor *sensor) { threshold_sensor_ = sensor; }
  void set_motion_binary_sensor(binary_sensor::BinarySensor *sensor) { motion_binary_sensor_ = sensor; }
  
  // Feature sensors
  void set_variance_sensor(sensor::Sensor *sensor) { variance_sensor_ = sensor; }
  void set_skewness_sensor(sensor::Sensor *sensor) { skewness_sensor_ = sensor; }
  void set_kurtosis_sensor(sensor::Sensor *sensor) { kurtosis_sensor_ = sensor; }
  void set_entropy_sensor(sensor::Sensor *sensor) { entropy_sensor_ = sensor; }
  void set_iqr_sensor(sensor::Sensor *sensor) { iqr_sensor_ = sensor; }
  void set_spatial_variance_sensor(sensor::Sensor *sensor) { spatial_variance_sensor_ = sensor; }
  void set_spatial_correlation_sensor(sensor::Sensor *sensor) { spatial_correlation_sensor_ = sensor; }
  void set_spatial_gradient_sensor(sensor::Sensor *sensor) { spatial_gradient_sensor_ = sensor; }
  void set_temporal_delta_mean_sensor(sensor::Sensor *sensor) { temporal_delta_mean_sensor_ = sensor; }
  void set_temporal_delta_variance_sensor(sensor::Sensor *sensor) { temporal_delta_variance_sensor_ = sensor; }
  
  /**
   * Publish all sensors with current values
   * 
   * @param processor CSI processor context (for motion data)
   * @param features Feature data (optional, can be nullptr if features disabled)
   * @param motion_state Current motion state
   */
  void publish_all(const csi_processor_context_t *processor,
                   const csi_features_t *features,
                   csi_motion_state_t motion_state);
  
  /**
   * Log status with progress bar
   * 
   * @param tag Log tag
   * @param processor CSI processor context
   * @param motion_state Current motion state
   * @param packets_per_publish Number of packets processed per publish cycle
   */
  void log_status(const char *tag,
                  const csi_processor_context_t *processor,
                  csi_motion_state_t motion_state,
                  uint32_t packets_per_publish);
  
  /**
   * Check if sensors are configured
   */
  bool has_movement_sensor() const { return movement_sensor_ != nullptr; }
  bool has_threshold_sensor() const { return threshold_sensor_ != nullptr; }
  bool has_motion_binary_sensor() const { return motion_binary_sensor_ != nullptr; }
  
 private:
  // Motion sensors
  sensor::Sensor *movement_sensor_{nullptr};
  sensor::Sensor *threshold_sensor_{nullptr};
  binary_sensor::BinarySensor *motion_binary_sensor_{nullptr};
  
  // Rate tracking
  uint32_t last_log_time_ms_{0};
  
  // Feature sensors
  sensor::Sensor *variance_sensor_{nullptr};
  sensor::Sensor *skewness_sensor_{nullptr};
  sensor::Sensor *kurtosis_sensor_{nullptr};
  sensor::Sensor *entropy_sensor_{nullptr};
  sensor::Sensor *iqr_sensor_{nullptr};
  sensor::Sensor *spatial_variance_sensor_{nullptr};
  sensor::Sensor *spatial_correlation_sensor_{nullptr};
  sensor::Sensor *spatial_gradient_sensor_{nullptr};
  sensor::Sensor *temporal_delta_mean_sensor_{nullptr};
  sensor::Sensor *temporal_delta_variance_sensor_{nullptr};
};

}  // namespace espectre
}  // namespace esphome
