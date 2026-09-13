#!/bin/sh
# Auto-installer script for TheWeather Enigma2 Plugin
# Repository: https://github.com/Caught/TheWeather

REPO_URL="https://github.com/Caught/TheWeather"
REPO_RAW="https://raw.githubusercontent.com/Caught/TheWeather/main"
TMP_DIR="/tmp"
DEFAULT_VER="4.4"

echo "=========================================="
echo "    Installing TheWeather Plugin...       "
echo "=========================================="

# 1. Detect package manager and determine file names
if command -v opkg >/dev/null 2>&1; then
    echo "-> OPKG package manager detected (IPK system)..."
    
    # Try to automatically find the latest .ipk filename from GitHub
    PACKAGE_FILE=$(wget -qO- "${REPO_URL}/tree/main" | grep -oE 'enigma2-plugin-extensions-theweather_[0-9]+\.[0-9]+_all\.ipk' | head -n 1)
    
    if [ -z "$PACKAGE_FILE" ]; then
        PACKAGE_FILE="enigma2-plugin-extensions-theweather_${DEFAULT_VER}_all.ipk"
    fi
    
    DOWNLOAD_URL="${REPO_RAW}/${PACKAGE_FILE}"
    
    cd ${TMP_DIR}
    rm -f enigma2-plugin-extensions-theweather_*.ipk
    
    echo "-> Downloading ${PACKAGE_FILE}..."
    wget -q "${DOWNLOAD_URL}" -O ${TMP_DIR}/${PACKAGE_FILE} || curl -sL "${DOWNLOAD_URL}" -o ${TMP_DIR}/${PACKAGE_FILE}
    
    if [ -f "${TMP_DIR}/${PACKAGE_FILE}" ]; then
        echo "-> Installing package..."
        opkg install --force-overwrite ${TMP_DIR}/${PACKAGE_FILE}
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        echo "-> Installation completed successfully!"
    else
        echo "-> ERROR: Failed to download ${PACKAGE_FILE}."
        exit 1
    fi

elif command -v dpkg >/dev/null 2>&1; then
    echo "-> DPKG package manager detected (DEB system / DreamOS)..."
    
    # Try to automatically find the latest .deb filename from GitHub
    PACKAGE_FILE=$(wget -qO- "${REPO_URL}/tree/main" | grep -oE 'enigma2-plugin-extensions-theweather_[0-9]+\.[0-9]+_all\.deb' | head -n 1)
    
    if [ -z "$PACKAGE_FILE" ]; then
        PACKAGE_FILE="enigma2-plugin-extensions-theweather_${DEFAULT_VER}_all.deb"
    fi
    
    DOWNLOAD_URL="${REPO_RAW}/${PACKAGE_FILE}"
    
    cd ${TMP_DIR}
    rm -f enigma2-plugin-extensions-theweather_*.deb
    
    echo "-> Downloading ${PACKAGE_FILE}..."
    wget -q "${DOWNLOAD_URL}" -O ${TMP_DIR}/${PACKAGE_FILE} || curl -sL "${DOWNLOAD_URL}" -o ${TMP_DIR}/${PACKAGE_FILE}
    
    if [ -f "${TMP_DIR}/${PACKAGE_FILE}" ]; then
        echo "-> Installing package..."
        dpkg -i ${TMP_DIR}/${PACKAGE_FILE}
        apt-get install -f -y >/dev/null 2>&1
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        echo "-> Installation completed successfully!"
    else
        echo "-> ERROR: Failed to download ${PACKAGE_FILE}."
        exit 1
    fi
else
    echo "-> ERROR: No supported package manager (opkg/dpkg) found on this system."
    exit 1
fi

# 2. Prompt for GUI restart
echo "=========================================="
printf "Do you want to restart the GUI (Enigma2) now? [y/N]: "
read RESTART < /dev/tty

case "$RESTART" in 
  y|Y|yes|YES ) 
    echo "-> Restarting GUI now..."
    if command -v init >/dev/null 2>&1; then
        init 4 && init 3
    else
        systemctl restart enigma2
    fi
    ;;
  * ) 
    echo "-> Restart skipped. Please remember to restart the GUI manually!"
    ;;
esac

exit 0