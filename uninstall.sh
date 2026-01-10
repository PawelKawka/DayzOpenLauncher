#!/bin/bash
INSTALL_DIR="$HOME/.local/share/DayzOpenLauncher"

echo "--- DayzOpenLauncher Linux Uninstaller ---"

DESKTOP_FILE="$HOME/.local/share/applications/dayzlauncher.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_FILE"
fi

DESKTOP_DIR=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
if [ -f "$DESKTOP_DIR/dayzlauncher.desktop" ]; then
    echo "Removing Desktop icon..."
    rm "$DESKTOP_DIR/dayzlauncher.desktop"
fi

if [ -f "$HOME/dayzopenlauncher.sh" ]; then
    echo "Removing entry script..."
    rm "$HOME/dayzopenlauncher.sh"
fi

CONFIG_DIR="$HOME/.config/DayzOpenLauncher"
if [ -d "$CONFIG_DIR" ]; then
    read -p "Do you want to remove all settings and favorites from .config? (y/N): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "Removing configuration..."
        rm -rf "$CONFIG_DIR"
    fi
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Removing installation folder at $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
fi

echo "Done"
