/*
 * ESPectre - Main Component Implementation
 * 
 * Main ESPHome component that orchestrates all ESPectre subsystems.
 * Integrates CSI processing, calibration, and Home Assistant publishing.
 * 
 * Author: Francesco Pace <francesco.pace@gmail.com>
 * License: GPLv3
 */

#include "espectre_component.h"
#include "utils.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"
#include "esp_wifi.h"
#include "esp_err.h"
#include <cstring>

namespace esphome {
namespace espectre {

void ESpectreComponent::setup() {
  ESP_LOGI(TAG, "Initializing ESPectre component...");
  
  // 0. Initialize WiFi for optimal CSI capture
  this->wifi_lifecycle_.init();
  
  // 1. Initialize configuration manager (load config before initializing managers)
  this->config_manager_.init(
      global_preferences->make_preference<ESpectreConfig>(fnv1_hash("espectre_cfg"))
  );
  
  // 2. Load configuration from preferences
  ESpectreConfig config;
  if (this->config_manager_.load(config)) {
    this->segmentation_threshold_ = config.segmentation_threshold;
    this->segmentation_window_size_ = config.segmentation_window_size;
    this->traffic_generator_rate_ = config.traffic_generator_rate;
    this->hampel_enabled_ = config.hampel_enabled;
    this->hampel_window_ = config.hampel_window;
    this->hampel_threshold_ = config.hampel_threshold;
  }
  
  // 3. Initialize CSI processor (allocates buffer internally)
  if (!csi_processor_init(&this->csi_processor_, 
                          this->segmentation_window_size_, 
                          this->segmentation_threshold_)) {
    ESP_LOGE(TAG, "Failed to initialize CSI processor");
    return;  // Component initialization failed
  }
  
  // 4. Initialize managers (each manager handles its own internal initialization)
  this->calibration_manager_.init(&this->csi_manager_);
  this->traffic_generator_.init(this->traffic_generator_rate_);
  this->csi_manager_.init(
    &this->csi_processor_,
    this->selected_subcarriers_,
    this->segmentation_threshold_,
    this->segmentation_window_size_,
    this->traffic_generator_rate_,
    this->hampel_enabled_,
    this->hampel_window_,
    this->hampel_threshold_
  );
  
  // 5. Register WiFi lifecycle handlers
  this->wifi_lifecycle_.register_handlers(
      [this]() { this->on_wifi_connected_(); },
      [this]() { this->on_wifi_disconnected_(); }
  );
  
  ESP_LOGI(TAG, "ESPectre initialized successfully");
}

ESpectreComponent::~ESpectreComponent() {
  // Cleanup CSI processor (deallocates turbulence buffer)
  csi_processor_cleanup(&this->csi_processor_);
}

void ESpectreComponent::on_wifi_connected_() {
  
  // Enable CSI using CSI Manager with periodic callback
  if (!this->csi_manager_.is_enabled()) {
    ESP_ERROR_CHECK(this->csi_manager_.enable(
      [this](csi_motion_state_t state) {

        // Don't publish until ready
        if (!this->ready_to_publish_) return;
        
        // Log status with progress bar and CSI rate
        this->sensor_publisher_.log_status(TAG, &this->csi_processor_, state, this->traffic_generator_rate_);
        
        // Publish all sensors
        this->sensor_publisher_.publish_all(&this->csi_processor_, state);
      }
    ));
  }
  
  // Start traffic generator
  ESP_LOGI(TAG, "Attempting to start traffic generator (rate: %u pps)...", this->traffic_generator_rate_);
  if (!this->traffic_generator_.is_running()) {
    if (!this->traffic_generator_.start()) {
      ESP_LOGW(TAG, "Failed to start traffic generator");
      return;
    }
    ESP_LOGI(TAG, "Traffic generator started successfully");
  } else {
    ESP_LOGI(TAG, "Traffic generator already running");
  }
  
  // Run auto-calibration if user didn't specify subcarriers
  if (this->traffic_generator_.is_running() && !this->user_specified_subcarriers_) {
    this->calibration_manager_.start_auto_calibration(
      this->selected_subcarriers_,
      12,  // Always 12 subcarriers
      [this](const uint8_t* band, uint8_t size, bool success) {
        if (success) {
          memcpy(this->selected_subcarriers_, band, size);
          this->csi_manager_.update_subcarrier_selection(band);
        }
      }
    );
  }
  
  // Ready to publish sensors
  if (this->traffic_generator_.is_running()) {
    this->ready_to_publish_ = true;
  }
}

void ESpectreComponent::on_wifi_disconnected_() {
  // Disable CSI using CSI Manager
  this->csi_manager_.disable();
  
  // Stop traffic generator
  if (this->traffic_generator_.is_running()) {
    this->traffic_generator_.stop();
  }
  
  // Reset flags
  this->ready_to_publish_ = false;
}

void ESpectreComponent::loop() {
  // Event-driven component: all processing handled by managers via callbacks
}

void ESpectreComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "ESPectre:");
  
  // Motion Detection Configuration
  ESP_LOGCONFIG(TAG, "  Motion Detection:");
  ESP_LOGCONFIG(TAG, "    Threshold: %.2f", this->segmentation_threshold_);
  ESP_LOGCONFIG(TAG, "    Window Size: %d packets", this->segmentation_window_size_);
  
  // Subcarrier Selection
  ESP_LOGCONFIG(TAG, "  Subcarriers: [%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d]",
                this->selected_subcarriers_[0], this->selected_subcarriers_[1],
                this->selected_subcarriers_[2], this->selected_subcarriers_[3],
                this->selected_subcarriers_[4], this->selected_subcarriers_[5],
                this->selected_subcarriers_[6], this->selected_subcarriers_[7],
                this->selected_subcarriers_[8], this->selected_subcarriers_[9],
                this->selected_subcarriers_[10], this->selected_subcarriers_[11]);
  ESP_LOGCONFIG(TAG, "    Source: %s", this->user_specified_subcarriers_ ? "User (YAML)" : "Auto-calibrated (NBVI)");
  
  // Traffic Generator
  ESP_LOGCONFIG(TAG, "  Traffic Generator:");
  ESP_LOGCONFIG(TAG, "    Rate: %u pps", this->traffic_generator_rate_);
  ESP_LOGCONFIG(TAG, "    Status: %s", this->traffic_generator_.is_running() ? "Running" : "Stopped");
  
  // Hampel Filter
  ESP_LOGCONFIG(TAG, "  Hampel Filter (Turbulence):");
  ESP_LOGCONFIG(TAG, "    Enabled: %s", this->hampel_enabled_ ? "YES" : "NO");
  if (this->hampel_enabled_) {
    ESP_LOGCONFIG(TAG, "    Window: %d packets", this->hampel_window_);
    ESP_LOGCONFIG(TAG, "    Threshold: %.1f MAD", this->hampel_threshold_);
  }
  
  // Sensors Status
  ESP_LOGCONFIG(TAG, "  Sensors:");
  ESP_LOGCONFIG(TAG, "    Movement: %s", this->sensor_publisher_.has_movement_sensor() ? "Configured" : "Not configured");
  ESP_LOGCONFIG(TAG, "    Motion Binary: %s", this->sensor_publisher_.has_motion_binary_sensor() ? "Configured" : "Not configured");
  ESP_LOGCONFIG(TAG, "    Threshold: %s", this->sensor_publisher_.has_threshold_sensor() ? "Configured" : "Not configured");
}

}  // namespace espectre
}  // namespace esphome
