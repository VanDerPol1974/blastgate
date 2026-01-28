#!/bin/bash
set -e

echo "=== BlastGate Installation startet ==="

# System aktualisieren
sudo apt update
sudo apt upgrade -y

# Benötigte Pakete
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  git \
  screen

# Python venv
cd pi_backend
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install flask pyserial

deactivate
cd ..

echo "=== Installation abgeschlossen ==="
echo "Autostart via systemd separat aktivieren"
