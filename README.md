# Polecat-Ralph

Create a cli tool to iterate on a developer design

## Ralph

`ralph` is a Python CLI tool created to iterate on a developer design. It is located in the `ralph-container` directory.

### Installation

To install `ralph`, navigate to the `ralph-container` directory and use poetry:

```bash
cd ralph-container
poetry install
```

### Usage

To verify the installation and see the version:

```bash
poetry run ralph version
```

This will output the current version of the application as defined in `pyproject.toml`.

### Development

To run the application in development mode:

```bash
ralph loop --secrets tests/test_data/secrets --config tests/test_data/config.yaml tests/workdirs/workdir0 tests/instructions0.md
```
