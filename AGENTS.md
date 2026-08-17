# Agent Guidance

## Project Scope

This repository is a custom HACS integration for Home Assistant that connects to a local Iungo energy monitor. User-facing installation and configuration details are in [README.md](README.md).

## Repository Map

- `custom_components/iungo/config_flow.py`: validates the configured host and creates or reconfigures entries.
- `custom_components/iungo/__init__.py`: creates the device, initializes coordinators, and forwards platform setup.
- `custom_components/iungo/coordinator.py`: owns 30-second data polling and 3600-second firmware polling.
- `custom_components/iungo/iungo.py`: owns Iungo HTTP requests, response parsing, and sensor-definition extraction.
- `custom_components/iungo/sensor.py`: maps Iungo properties to Home Assistant sensors, including calculated energy and water sensors.
- `custom_components/iungo/update.py`: exposes firmware information as a read-only update entity.
- `custom_components/iungo/translations/`: contains config-flow translations; keep `en.json` and `nl.json` aligned when adding user-visible flow text.
- `custom_components/iungo/manifest.json`: integration metadata and version.

## Implementation Conventions

- Keep network access asynchronous and use Home Assistant's shared aiohttp session.
- Keep Iungo endpoint URLs and polling intervals in `const.py`.
- Convert transport/API failures to the integration's `IungoError` hierarchy in `iungo.py`; coordinators translate those failures into Home Assistant coordinator errors.
- Preserve the response contract: Iungo API responses are read from the `rv` field, and object values are normalized to `{object_id: {property_id: value}}`.
- Preserve stable entity IDs. Regular sensors use `{object_id}_{prop_id}`; firmware entities use the config-entry ID.
- When changing sensor units or mappings, update the related device class, state class, and display precision maps together.
- Avoid unrelated formatting or refactoring in this small integration. Follow the existing Home Assistant entity and coordinator patterns.

## Validation

There is no test suite or lint configuration in this repository. Before submitting Python changes, run:

```text
python -m compileall custom_components/iungo
```

Pushes and pull requests run the authoritative checks defined in [hassfest.yaml](.github/workflows/hassfest.yaml) and [validate-hacs.yaml](.github/workflows/validate-hacs.yaml): Home Assistant hassfest validation and HACS integration validation.

For changes to config flow behavior, translations, manifest metadata, or entity schemas, inspect the corresponding Home Assistant and HACS validation output rather than assuming local compilation is sufficient.