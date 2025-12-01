# MicroPython Firmware with CSI Support

This directory contains precompiled MicroPython firmware with the `microcsi` module integrated.

## Available Firmware

| File | Chip | micropython-esp32-csi Version | Build Date |
|------|------|---------------------|------------------|------------|
| ESP32_GENERIC_S3.bin | ESP32-S3 | v1.0.0 | 2025-01-12 |
| ESP32_GENERIC_C6.bin | ESP32-C6 | v1.0.0 | 2025-01-12 |

## Usage

The firmware files are automatically detected by the `me` CLI tool:

```bash
# Flash autodetecting port and ESP32 model
./me flash --erase
```

## Building from Source

If you prefer to build the firmware yourself, follow the instructions at:
https://github.com/francescopace/micropython-esp32-csi

## File Sizes

- ESP32_GENERIC_S3.bin: ~1.8 MB
- ESP32_GENERIC_C6.bin: ~1.6 MB

## Notes

- The firmware is built from the official MicroPython repository with the esp32-csi` module integrated
- No additional installation is required after flashing