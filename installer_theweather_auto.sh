#!/bin/sh
set -e

REPO="Caught/TheWeather"
NAME="theweather"
VERSION="4.1"

if command -v dpkg >/dev/null 2>&1; then
    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.deb"
    URL="https://raw.githubusercontent.com/${REPO}/main/deb/${PKG}"
    echo "Downloading $PKG ..."
    wget -q -O "/tmp/${PKG}" "$URL"
    dpkg -i "/tmp/${PKG}"
    rm -f "/tmp/${PKG}"
elif command -v opkg >/dev/null 2>&1; then
    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.ipk"
    URL="https://raw.githubusercontent.com/${REPO}/main/ipk/${PKG}"
    echo "Downloading $PKG ..."
    wget -q -O "/tmp/${PKG}" "$URL"
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