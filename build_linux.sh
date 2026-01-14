#!/bin/bash
set -e

APP_NAME="DayzOpenLauncher"

echo "building $APP_NAME for linux..."

echo "[*] checking/installing dep..."
python3 -m pip install --upgrade pip
python3 -m pip install rich prompt_toolkit requests python-a2s pyinstaller

rm -rf build dist

PYINSTALLER="python3 -m PyInstaller"

$PYINSTALLER --noconfirm --onedir --clean --name "$APP_NAME" \
    Source/main.py

echo "[*] building updater..."
$PYINSTALLER --noconfirm --onefile --clean --name "updater" \
    Source/linux/updater.py

cp "dist/updater" "dist/$APP_NAME/"

if [ -f "steam_appid.txt" ]; then
    cp "steam_appid.txt" "dist/$APP_NAME/"
else
    echo "221100" > "dist/$APP_NAME/steam_appid.txt"
fi

VERSION="1.1.0"
echo "$VERSION" > "dist/$APP_NAME/version.txt"
echo "$VERSION" > "version.txt"

echo "creating release package..."
mkdir -p dayzopenlauncher-linux
cp -r "dist/$APP_NAME" dayzopenlauncher-linux/
cp version.txt dayzopenlauncher-linux/

echo "packaging into zip..."
zip -r dayzopenlauncher-linux.zip dayzopenlauncher-linux/
rm -rf dayzopenlauncher-linux/

echo "build complete"
