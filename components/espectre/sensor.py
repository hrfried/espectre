"""
ESPectre Sensor Platform

ESPHome sensor platform for ESPectre motion detection metrics.
Provides movement intensity and threshold sensors.

Author: Francesco Pace <francesco.pace@gmail.com>
License: GPLv3
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_ID,
    STATE_CLASS_MEASUREMENT,
    UNIT_EMPTY,
)
from . import (
    espectre_ns,
    ESpectreComponent,
    CONF_MOVEMENT,
    CONF_THRESHOLD,
)

DEPENDENCIES = ["espectre"]

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.use_id(ESpectreComponent),
    
    # Core sensors
    cv.Optional(CONF_MOVEMENT): sensor.sensor_schema(
        unit_of_measurement=UNIT_EMPTY,
        accuracy_decimals=2,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    cv.Optional(CONF_THRESHOLD): sensor.sensor_schema(
        unit_of_measurement=UNIT_EMPTY,
        accuracy_decimals=2,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
})

async def to_code(config):
    parent = await cg.get_variable(config[CONF_ID])
    
    # Core sensors
    if CONF_MOVEMENT in config:
        sens = await sensor.new_sensor(config[CONF_MOVEMENT])
        cg.add(parent.set_movement_sensor(sens))
    
    if CONF_THRESHOLD in config:
        sens = await sensor.new_sensor(config[CONF_THRESHOLD])
        cg.add(parent.set_threshold_sensor(sens))
