# Iungo Home Assistant Integration

## Overview
The Iungo integration for Home Assistant allows users to connect and manage their Iungo devices seamlessly within the Home Assistant ecosystem.

## Installation
1. Clone this repository to your Home Assistant `custom_components` directory:
   ```
   git clone https://github.com/yourusername/ha-iungo.git
   ```
2. Ensure that the `ha-iungo` folder is located in your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/iungo
   ```

3. Install the required Python packages listed in `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```

## Configuration
To set up the Iungo integration, add the following to your `configuration.yaml` file:

```yaml
iungo:
  # Add your configuration options here
```

## Usage
Once the integration is installed and configured, you can start using the Iungo sensors and other features within Home Assistant. The integration will automatically discover your Iungo devices.

## Contributing
If you would like to contribute to the Iungo integration, please fork the repository and submit a pull request. We welcome contributions that improve functionality, fix bugs, or enhance documentation.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.