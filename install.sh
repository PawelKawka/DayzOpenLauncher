#!/bin/bash
set -e

echo "--- DayzOpenLauncher Linux Installer ---"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed."
    exit 1
fi

SOURCE_DIR=$(pwd)
INSTALL_DIR="$HOME/.local/share/DayzOpenLauncher"
VENV_DIR="$INSTALL_DIR/.venvdol"
LAUNCHER_SCRIPT="$HOME/dayzopenlauncher.sh"
DESKTOP_FILE="$HOME/.local/share/applications/dayzlauncher.desktop"

if [ -d "$INSTALL_DIR" ] || [ -f "$LAUNCHER_SCRIPT" ] || [ -f "$DESKTOP_FILE" ]; then
    read -p "Launcher already installed. Do you want to reinstall? (y/N): " choice
    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

mkdir -p "$INSTALL_DIR"

for item in "Source" "assets" "uninstall.sh" "steam_appid.txt"; do
    if [ -e "$SOURCE_DIR/$item" ]; then
        cp -rL "$SOURCE_DIR/$item" "$INSTALL_DIR/"
        if [ "$item" == "Source" ]; then
            rm -rf "$INSTALL_DIR/Source/windows"
        fi
    fi
done

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" || { echo "Error: Failed to create venv. Install python3-venv"; exit 1; }
fi

REQUIRED_MODULES=("rich" "prompt_toolkit" "requests" "python-a2s")
INSTALLED_MODULES=$("$VENV_DIR/bin/pip" list --format freeze)

for module in "${REQUIRED_MODULES[@]}"; do
    if ! echo "$INSTALLED_MODULES" | grep -qi "^${module}=="; then
        echo "Installing $module..."
        "$VENV_DIR/bin/pip" install -q "$module"
    fi
done

LAUNCHER_SCRIPT="$HOME/dayzopenlauncher.sh"
cat <<EOF > "$LAUNCHER_SCRIPT"
#!/bin/bash
cd "$INSTALL_DIR" || exit 1

chmod +x "$INSTALL_DIR/Source/main.py" 2>/dev/null || true

"$INSTALL_DIR/.venvdol/bin/python" "$INSTALL_DIR/Source/main.py"

if [ \$? -ne 0 ]; then
    echo ""
    echo "------------------------------------------"
    echo "Launcher crashed or failed to start."
    echo "Check if all dependencies are installed."
    echo "Press Enter to close this window..."
    read
fi
EOF
chmod +x "$LAUNCHER_SCRIPT"

DESKTOP_FILE="$HOME/.local/share/applications/dayzlauncher.desktop"
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=DayzOpenLauncher
Comment=Dayz TUI Launcher
Exec="$LAUNCHER_SCRIPT"
Path=$INSTALL_DIR
Icon=$INSTALL_DIR/assets/icon.png
Terminal=true
Categories=Game;
StartupNotify=false
EOF

chmod +x "$DESKTOP_FILE"

read -p "Do you want to create a launcher icon on your Desktop? (y/N): " desktop_choice
if [[ "$desktop_choice" =~ ^[Yy]$ ]]; then
    DESKTOP_DIR=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
    DESKTOP_ICON="$DESKTOP_DIR/dayzlauncher.desktop"
    cp "$DESKTOP_FILE" "$DESKTOP_ICON"
    chmod +x "$DESKTOP_ICON"
    
    # trusted mark
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_ICON" metadata::trusted true 2>/dev/null || true
    fi
    echo "Desktop icon created."
fi

echo "Done"
