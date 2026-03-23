# DASS Assignment 2

## Submission Links

- Google Drive: `<ADD_GOOGLE_DRIVE_LINK_HERE>`
- GitHub Repository: `<ADD_GITHUB_REPO_LINK_HERE>`

## Repository Overview

This repository contains the three testing parts of the assignment:

- `whitebox/` for the MoneyPoly whitebox analysis and pytest suite
- `blackbox/` for the QuickCart API blackbox suite and report
- `integration/` for the StreetRace Manager integration testing work

## Whitebox Testing

Run the whitebox work from the repository root.

### Install Dependencies

```bash
python3 -m pip install pytest pylint
```

### Run Pylint on the MoneyPoly Source

```bash
PYLINTHOME=/tmp/pylint PYTHONPATH=whitebox/code/moneypoly pylint \
  whitebox/code/moneypoly/main.py \
  whitebox/code/moneypoly/moneypoly/bank.py \
  whitebox/code/moneypoly/moneypoly/board.py \
  whitebox/code/moneypoly/moneypoly/cards.py \
  whitebox/code/moneypoly/moneypoly/config.py \
  whitebox/code/moneypoly/moneypoly/dice.py \
  whitebox/code/moneypoly/moneypoly/game.py \
  whitebox/code/moneypoly/moneypoly/player.py \
  whitebox/code/moneypoly/moneypoly/property.py \
  whitebox/code/moneypoly/moneypoly/ui.py
```

### Run the Whitebox Pytest Suite

```bash
python3 -m pytest whitebox/tests -q
```

## Blackbox Testing

### Start QuickCart

On Apple Silicon / ARM64 machines:

```bash
docker load -i quickcart_image.tar
docker run --rm --name quickcart-blackbox -p 8080:8080 quickcart:latest
```

On x86_64 machines:

```bash
docker load -i quickcart_image_x86.tar
docker run --rm --name quickcart-blackbox -p 8080:8080 quickcart:latest
```

### Run the Blackbox Tests

```bash
python3 -m pytest blackbox/tests -v
```

Optional environment variables:

- `QUICKCART_BASE_URL` defaults to `http://127.0.0.1:8080`
- `ROLL_NUMBER` defaults to `23110001`

## Integration Testing

### Run the StreetRace Manager Demo CLI

```bash
python3 -m integration.code.cli
```

### Run the Integration Test Suite

```bash
python3 -m pytest integration/tests -v
```
