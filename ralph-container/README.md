# ralph

A CLI tool to iterate on a developer design.

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run ralph version
```


# Example of running the ralph loop

```bash
ralph loop --secrets tests/test_data/secrets --config tests/test_data/config.yaml tests/workdirs/workdir0 tests/instructions0.md
```
