#!/bin/bash

# 1. Überprüfen, ob Python3 installiert ist
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found, please install Python3 to proceed."
    exit
fi

# 2. Erstelle eine virtuelle Umgebung
echo "Creating virtual environment..."
python3 -m venv venv

# 3. Aktivieren der virtuellen Umgebung
echo "Activating virtual environment..."
source venv/bin/activate

# 4. Installieren der Abhängigkeiten aus der requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# 5. Starten des Hauptprogramms
echo "Starting the application for the first time..."
python src/main.py

# Hinweis: Das Skript beendet die virtuelle Umgebung nicht automatisch, du kannst sie manuell verlassen, wenn du möchtest.