# Whitebox Execution

Run the whitebox work from the repository root.

## Install dependencies

```bash
python3 -m pip install pytest pylint
```

## Run pylint on the MoneyPoly source

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

## Run the whitebox pytest suite

```bash
python3 -m pytest whitebox/tests -q
```
