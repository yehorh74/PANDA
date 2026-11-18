#!/usr/bin/env bash
set -o errexit

echo "--- Pobieranie Flutter SDK (wersja 3.47.9) ---"
git clone https://github.com/flutter/flutter.git -b 3.47.9 --depth 1 _flutter
export PATH="$PATH:$(pwd)/_flutter/bin"

flutter config --no-analytics
flutter precache --web

echo "--- Instalacja zależności Pythona ---"
pip install --upgrade pip
pip install flet -r requirements.txt

echo "--- Budowanie aplikacji Flet Web ---"
export FLET_NON_INTERACTIVE="true"
flet build web --build-number 1 -o dist/web
