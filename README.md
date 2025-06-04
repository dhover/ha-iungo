# Iungo Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

This is a custom integration for [Home Assistant](https://www.home-assistant.io/) to connect with your Iungo energy monitor.

---

## Features

- Adds sensors for all Iungo objects and properties
- Supports calculated sensors for breakout energy and water
- Friendly names from your Iungo configuration
- Device classes, units, and display precision mapping

---

## Installation

### 1. Add this repository to HACS

1. Go to **HACS > Integrations** in Home Assistant.
2. Click the three dots (upper right) and select **Custom repositories**.
3. Add the URL of this repository:
   ```
   https://github.com/dhover/ha-iungo
   ```
   as type **Integration**.
4. Search for "Iungo" in HACS and install.

### 2. Restart Home Assistant

After installation, restart Home Assistant to load the integration.

### 3. Add the Integration

- Go to **Settings > Devices & Services > Add Integration**.
- Search for **Iungo** and follow the setup flow.

---

## Configuration

- Enter the host/IP address of your Iungo device.
- Sensors will be automatically discovered and added.

---

## Updating

- Update via HACS when a new version is available.

---

## Support

- Issues and feature requests: [GitHub Issues](https://github.com/dhover/ha-iungo/issues)

---

## Credits

- [@dhover](https://github.com/dhover)

---

## Disclaimer

This integration is not affiliated with or endorsed by Iungo. Use at your own risk.