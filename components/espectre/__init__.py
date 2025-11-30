import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, binary_sensor
from esphome.const import (
    CONF_ID,
)

DEPENDENCIES = ["wifi"]
AUTO_LOAD = ["sensor", "binary_sensor"]

# Configuration parameters
CONF_SEGMENTATION_THRESHOLD = "segmentation_threshold"
CONF_SEGMENTATION_WINDOW_SIZE = "segmentation_window_size"
CONF_TRAFFIC_GENERATOR_RATE = "traffic_generator_rate"
CONF_SELECTED_SUBCARRIERS = "selected_subcarriers"

# Hampel filter
CONF_HAMPEL_ENABLED = "hampel_enabled"
CONF_HAMPEL_WINDOW = "hampel_window"
CONF_HAMPEL_THRESHOLD = "hampel_threshold"

# Sensors
CONF_MOVEMENT = "movement"
CONF_THRESHOLD = "threshold"
CONF_MOTION = "motion"

espectre_ns = cg.esphome_ns.namespace("espectre")
ESpectreComponent = espectre_ns.class_("ESpectreComponent", cg.Component)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ESpectreComponent),
    
    # Motion detection
    cv.Optional(CONF_SEGMENTATION_THRESHOLD, default=1.0): cv.float_range(min=0.5, max=10.0),
    cv.Optional(CONF_SEGMENTATION_WINDOW_SIZE, default=50): cv.int_range(min=10, max=200),
    
    # Traffic generator (ESSENTIAL!)
    cv.Optional(CONF_TRAFFIC_GENERATOR_RATE, default=100): cv.int_range(min=0, max=1000),
    
    # Subcarrier selection (optional - if not specified, auto-calibrates at every boot)
    cv.Optional(CONF_SELECTED_SUBCARRIERS): cv.All(
        cv.ensure_list(cv.int_range(min=0, max=63)),
        cv.Length(min=1, max=12)
    ),
    
    # Hampel filter for turbulence outlier removal (aligned with Micro-ESPectre)
    cv.Optional(CONF_HAMPEL_ENABLED, default=True): cv.boolean,
    cv.Optional(CONF_HAMPEL_WINDOW, default=7): cv.int_range(min=3, max=11),
    cv.Optional(CONF_HAMPEL_THRESHOLD, default=4.0): cv.float_range(min=1.0, max=10.0),
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    
    # Add C++ source files to build
    cg.add_library(
        "espectre_core",
        None,
        [
            "config_manager.cpp",
            "wifi_lifecycle.cpp",
            "traffic_generator_manager.cpp",
            "sensor_publisher.cpp",
            "calibration_manager.cpp",
            "csi_manager.cpp",
            "csi_processor.cpp",
        ]
    )
    
    # Configure parameters
    cg.add(var.set_segmentation_threshold(config[CONF_SEGMENTATION_THRESHOLD]))
    cg.add(var.set_segmentation_window_size(config[CONF_SEGMENTATION_WINDOW_SIZE]))
    cg.add(var.set_traffic_generator_rate(config[CONF_TRAFFIC_GENERATOR_RATE]))
    
    # Configure subcarriers if specified
    if CONF_SELECTED_SUBCARRIERS in config:
        cg.add(var.set_selected_subcarriers(config[CONF_SELECTED_SUBCARRIERS]))
    
    # Configure Hampel filter
    cg.add(var.set_hampel_enabled(config[CONF_HAMPEL_ENABLED]))
    cg.add(var.set_hampel_window(config[CONF_HAMPEL_WINDOW]))
    cg.add(var.set_hampel_threshold(config[CONF_HAMPEL_THRESHOLD]))
