/*
 * ESPectre - CSI Processor Unit Tests
 *
 * Unit tests for the csi_processor module (initialization, parameters, reset, edge cases)
 * Motion detection performance is tested in test_performance.cpp
 *
 * Author: Francesco Pace <francesco.pace@gmail.com>
 * License: GPLv3
 */

#include <unity.h>
#include <string.h>

// Include headers from lib/espectre
#include "csi_processor.h"
#include "esp_log.h"
#include "esp_system.h"

using namespace esphome::espectre;

// Include CSI data
#include "real_csi_data_esp32.h"
#include "real_csi_arrays.inc"

static const char *TAG = "test_csi_processor";

// Default subcarrier selection (production configuration)
static const uint8_t SELECTED_SUBCARRIERS[] = {11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22};
static const uint8_t NUM_SUBCARRIERS = sizeof(SELECTED_SUBCARRIERS) / sizeof(SELECTED_SUBCARRIERS[0]);

void setUp(void) {
    // Setup before each test
}

void tearDown(void) {
    // Cleanup after each test
}

// Helper function to process a packet
static void process_packet(csi_processor_context_t *ctx, const int8_t *packet) {
    csi_process_packet(ctx, packet, 128, SELECTED_SUBCARRIERS, NUM_SUBCARRIERS);
}

// Test: Initialize CSI processor context
void test_segmentation_init(void) {
    csi_processor_context_t ctx;

    TEST_ASSERT_TRUE(csi_processor_init(&ctx, SEGMENTATION_DEFAULT_WINDOW_SIZE, SEGMENTATION_DEFAULT_THRESHOLD));

    TEST_ASSERT_EQUAL(CSI_STATE_IDLE, ctx.state);
    TEST_ASSERT_EQUAL(0, ctx.buffer_count);
    TEST_ASSERT_TRUE(ctx.threshold > 0.0f);
    TEST_ASSERT_EQUAL(SEGMENTATION_DEFAULT_WINDOW_SIZE, ctx.window_size);
}

// Test: Parameter setters and getters
void test_segmentation_parameters(void) {
    csi_processor_context_t ctx;
    
    // Test window size is set at init and cannot be changed
    TEST_ASSERT_TRUE(csi_processor_init(&ctx, 10, SEGMENTATION_DEFAULT_THRESHOLD));
    TEST_ASSERT_EQUAL(10, csi_processor_get_window_size(&ctx));
    csi_processor_cleanup(&ctx);
    
    TEST_ASSERT_TRUE(csi_processor_init(&ctx, 200, SEGMENTATION_DEFAULT_THRESHOLD));
    TEST_ASSERT_EQUAL(200, csi_processor_get_window_size(&ctx));
    csi_processor_cleanup(&ctx);
    
    // Test invalid window size (too small) - init should fail
    TEST_ASSERT_FALSE(csi_processor_init(&ctx, 0, SEGMENTATION_DEFAULT_THRESHOLD));
    
    // Test invalid window size (too large) - init should fail
    TEST_ASSERT_FALSE(csi_processor_init(&ctx, 201, SEGMENTATION_DEFAULT_THRESHOLD));

    // Test threshold setter/getter
    TEST_ASSERT_TRUE(csi_processor_init(&ctx, SEGMENTATION_DEFAULT_WINDOW_SIZE, SEGMENTATION_DEFAULT_THRESHOLD));
    
    TEST_ASSERT_TRUE(csi_processor_set_threshold(&ctx, 0.5f));
    TEST_ASSERT_EQUAL_FLOAT(0.5f, csi_processor_get_threshold(&ctx));

    TEST_ASSERT_TRUE(csi_processor_set_threshold(&ctx, 2.0f));
    TEST_ASSERT_EQUAL_FLOAT(2.0f, csi_processor_get_threshold(&ctx));

    // Test invalid threshold (negative)
    TEST_ASSERT_FALSE(csi_processor_set_threshold(&ctx, -1.0f));
    TEST_ASSERT_EQUAL_FLOAT(2.0f, csi_processor_get_threshold(&ctx));  // Should remain unchanged
    
    csi_processor_cleanup(&ctx);
}

// Test: Reset functionality preserves parameters
void test_segmentation_reset(void) {
    csi_set_subcarrier_selection(SELECTED_SUBCARRIERS, NUM_SUBCARRIERS);

    csi_processor_context_t ctx;
    TEST_ASSERT_TRUE(csi_processor_init(&ctx, 30, SEGMENTATION_DEFAULT_THRESHOLD));

    // Configure custom threshold
    csi_processor_set_threshold(&ctx, 1.5f);

    // Process some packets to change state
    for (int i = 0; i < 50 && i < num_movement; i++) {
        process_packet(&ctx, (const int8_t*)movement_packets[i]);
    }

    // Store configured parameters
    float threshold_before = csi_processor_get_threshold(&ctx);
    uint16_t window_before = csi_processor_get_window_size(&ctx);

    // Reset
    csi_processor_reset(&ctx);

    // Verify state is reset
    TEST_ASSERT_EQUAL(CSI_STATE_IDLE, ctx.state);
    TEST_ASSERT_EQUAL(0, ctx.packet_index);

    // Verify parameters are preserved
    TEST_ASSERT_EQUAL_FLOAT(threshold_before, csi_processor_get_threshold(&ctx));
    TEST_ASSERT_EQUAL(window_before, csi_processor_get_window_size(&ctx));
}

// Test: Handles invalid input gracefully
void test_segmentation_handles_invalid_input(void) {
    csi_processor_context_t ctx;
    TEST_ASSERT_TRUE(csi_processor_init(&ctx, SEGMENTATION_DEFAULT_WINDOW_SIZE, SEGMENTATION_DEFAULT_THRESHOLD));

    // Test with NULL data - should handle gracefully without crash
    csi_process_packet(&ctx, NULL, 128, SELECTED_SUBCARRIERS, NUM_SUBCARRIERS);
    TEST_ASSERT_EQUAL(CSI_STATE_IDLE, ctx.state);

    // Test with zero length
    int8_t dummy[128] = {0};
    csi_process_packet(&ctx, dummy, 0, SELECTED_SUBCARRIERS, NUM_SUBCARRIERS);
    TEST_ASSERT_EQUAL(CSI_STATE_IDLE, ctx.state);

    // Test with NULL subcarriers
    csi_process_packet(&ctx, dummy, 128, NULL, 0);
    TEST_ASSERT_EQUAL(CSI_STATE_IDLE, ctx.state);
}

// Test: Stress test with many packets and memory leak check
void test_segmentation_stress_test(void) {
    csi_set_subcarrier_selection(SELECTED_SUBCARRIERS, NUM_SUBCARRIERS);

    // Measure heap before test
    size_t heap_before = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Heap before stress test: %zu bytes", heap_before);

    csi_processor_context_t ctx;
    TEST_ASSERT_TRUE(csi_processor_init(&ctx, SEGMENTATION_DEFAULT_WINDOW_SIZE, SEGMENTATION_DEFAULT_THRESHOLD));

    // Process all available packets multiple times
    int total_packets = 0;
    int total_motion = 0;

    for (int round = 0; round < 5; round++) {
        // Process baseline
        for (int i = 0; i < num_baseline; i++) {
            process_packet(&ctx, (const int8_t*)baseline_packets[i]);
            total_packets++;
            if (csi_processor_get_state(&ctx) == CSI_STATE_MOTION) {
                total_motion++;
            }
        }

        // Process movement
        for (int i = 0; i < num_movement; i++) {
            process_packet(&ctx, (const int8_t*)movement_packets[i]);
            total_packets++;
            if (csi_processor_get_state(&ctx) == CSI_STATE_MOTION) {
                total_motion++;
            }
        }
    }

    // Measure heap after test
    size_t heap_after = esp_get_free_heap_size();
    int heap_diff = (int)heap_before - (int)heap_after;

    ESP_LOGI(TAG, "Stress test: %d packets processed, %d motion (%.1f%%)",
             total_packets, total_motion, (total_motion * 100.0f) / total_packets);
    ESP_LOGI(TAG, "Heap after stress test: %zu bytes (diff: %d bytes)",
             heap_after, heap_diff);

    // Should have processed all packets without crash
    TEST_ASSERT_EQUAL(10000, total_packets);  // 5 rounds * 2000 packets

    // Should have detected some motion
    TEST_ASSERT_GREATER_THAN(0, total_motion);

    // Memory leak check: allow up to 1KB tolerance for fragmentation
    TEST_ASSERT_LESS_THAN(1024, heap_diff);
}

int process(void) {
    UNITY_BEGIN();
    RUN_TEST(test_segmentation_init);
    RUN_TEST(test_segmentation_parameters);
    RUN_TEST(test_segmentation_reset);
    RUN_TEST(test_segmentation_handles_invalid_input);
    RUN_TEST(test_segmentation_stress_test);
    return UNITY_END();
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
