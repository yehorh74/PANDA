#!/usr/bin/env bash
set -o errexit

echo "--- Konfiguracja stabilnej wersji Pythona (3.11.9) ---"
if command -v asdf &> /dev/null; then
    asdf plugin add python || true
    asdf install python 3.11.9
    asdf local python 3.11.9
    asdf reshim python
fi

echo "--- Weryfikacja wersji Pythona ---"
python --version
python -m pip --version

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
