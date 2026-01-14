#!/bin/bash
set -e

APP_NAME="DayzOpenLauncher"
REPO="PawelKawka/dev.dol"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="/usr/local/bin"

if [ ! -w "$BIN_DIR" ]; then
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
fi

echo "DayzOpenLauncher Installer"
echo "Fetching latest release..."
RELEASE_JSON=$(curl -s "https://api.github.com/repos/$REPO/releases/latest")
DOWNLOAD_URL=$(echo "$RELEASE_JSON" | grep -o 'https://github.com/[^"]*linux.zip' | head -n 1)
VERSION=$(echo "$RELEASE_JSON" | grep -o '"tag_name": "[^"]*"' | head -n 1 | cut -d'"' -f4)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "Error: Could not find linux.zip in latest release."
    exit 1
fi

TMP_ZIP="/tmp/dayz_launcher.zip"
TMP_DIR="/tmp/dayz_launcher_extract"
rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"

echo "Downloading DayzOpenLauncher $VERSION..."
curl -L -s -o "$TMP_ZIP" "$DOWNLOAD_URL"
unzip -q -o "$TMP_ZIP" -d "$TMP_DIR"

echo "Extracting application files..."
REAL_BINARY=$(find "$TMP_DIR" -type f -name "DayzOpenLauncher" | head -n 1)

if [ -z "$REAL_BINARY" ] || [ ! -f "$REAL_BINARY" ]; then
    echo "Error: Binary 'DayzOpenLauncher' not found in the downloaded package."
    exit 1
fi

BINARY_SOURCE_DIR=$(dirname "$REAL_BINARY")

echo "Installing to $INSTALL_DIR..."
rm -rf "$INSTALL_DIR" && mkdir -p "$INSTALL_DIR"
cp -a "$BINARY_SOURCE_DIR/." "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/DayzOpenLauncher"

echo "Creating system command 'dayzopenlauncher'..."
if [ -w "$BIN_DIR" ]; then
    ln -sf "$INSTALL_DIR/DayzOpenLauncher" "$BIN_DIR/dayzopenlauncher"
else
    if command -v sudo >/dev/null 2>&1; then
        echo "Root privileges required to link to /usr/local/bin..."
        sudo ln -sf "$INSTALL_DIR/DayzOpenLauncher" "/usr/local/bin/dayzopenlauncher"
    else
        echo "Warning: cannot link to /usr/local/bin (no sudo). Linking to ~/.local/bin instead."
        mkdir -p "$HOME/.local/bin"
        ln -sf "$INSTALL_DIR/DayzOpenLauncher" "$HOME/.local/bin/dayzopenlauncher"
    fi
fi

# cleanup
rm -f "$TMP_ZIP"
rm -rf "$TMP_DIR"

echo ""
echo "Installation completed successfully! Version $VERSION is now installed."
echo "You can now launch the application with: dayzopenlauncher"