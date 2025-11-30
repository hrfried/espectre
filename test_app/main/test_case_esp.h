/*
 * ESPectre - Custom TEST_CASE Macro for ESP-IDF
 * 
 * Custom TEST_CASE macro that exports test descriptors.
 * Uses symbolic names instead of line numbers for better maintainability.
 * Required because standard TEST_CASE uses static storage and constructor
 * attributes which don't work properly in ESP-IDF.
 * 
 * Author: Francesco Pace <francesco.pace@gmail.com>
 * License: GPLv3
 */

#ifndef TEST_CASE_ESP_H
#define TEST_CASE_ESP_H

#include "unity.h"
#include "unity_test_runner.h"

// Custom TEST_CASE that uses symbolic names instead of line numbers
#define TEST_CASE_ESP(test_name_, desc_) \
    static void test_func_##test_name_(void); \
    test_desc_t test_desc_##test_name_ = { \
        .name = #test_name_, \
        .desc = desc_, \
        .fn = (test_func[]){&test_func_##test_name_}, \
        .file = __FILE__, \
        .line = __LINE__, \
        .test_fn_count = 1, \
        .test_fn_name = NULL, \
        .next = NULL \
    }; \
    static void test_func_##test_name_(void)

#endif // TEST_CASE_ESP_H
