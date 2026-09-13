#!/bin/sh
set -e

REPO="Caught/TheWeather"
NAME="theweather"
VERSION="4.4"

download_and_check() {
    URL="$1"
    DEST="$2"
    echo "Downloading $(basename "$DEST") ..."
    if ! wget --no-check-certificate -O "$DEST" "$URL"; then
        echo ""
        echo "ERROR: download failed (wget error) for:"
        echo "  $URL"
        rm -f "$DEST"
        exit 1
    fi
    SIZE=$(wc -c < "$DEST" 2>/dev/null || echo 0)
    if [ "$SIZE" -lt 1000 ]; then
        echo ""
        echo "ERROR: downloaded file is too small ($SIZE bytes) - likely a failed"
        echo "download or an invalid URL:"
        echo "  $URL"
        rm -f "$DEST"
        exit 1
    fi
}

if command -v dpkg >/dev/null 2>&1; then
    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.deb"
    URL="https://raw.githubusercontent.com/${REPO}/main/deb/${PKG}"
    download_and_check "$URL" "/tmp/${PKG}"
    dpkg -i "/tmp/${PKG}"
    rm -f "/tmp/${PKG}"
elif command -v opkg >/dev/null 2>&1; then
    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.ipk"
    URL="https://raw.githubusercontent.com/${REPO}/main/ipk/${PKG}"
    download_and_check "$URL" "/tmp/${PKG}"
    opkg install --force-reinstall --force-downgrade --force-overwrite "/tmp/${PKG}"
    rm -f "/tmp/${PKG}"
else
    echo "No opkg or dpkg found — cannot proceed with installation."
    exit 1
fi

echo ""
echo "======================================================="
echo " Installation of TheWeather v${VERSION} completed!"
echo " Please restart Enigma2 (GUI) to activate the plugin."
echo "======================================================="
echo ""
