#!/bin/sh
set -e

REPO="Caught/TheWeather"
NAME="theweather"
VERSION="1.0"

if command -v opkg >/dev/null 2>&1; then
    PKG="${NAME}_${VERSION}_all.ipk"
    URL="https://raw.githubusercontent.com/${REPO}/main/ipk/${PKG}"
    echo "Downloading $PKG ..."
    wget -q -O "/tmp/${PKG}" "$URL"
    opkg install "/tmp/${PKG}"
elif command -v dpkg >/dev/null 2>&1; then
    PKG="${NAME}_${VERSION}_all.deb"
    URL="https://raw.githubusercontent.com/${REPO}/main/deb/${PKG}"
    echo "Downloading $PKG ..."
    wget -q -O "/tmp/${PKG}" "$URL"
    dpkg -i "/tmp/${PKG}"
else
    echo "Geen opkg of dpkg gevonden — kan niet installeren."
    exit 1
fi

echo "Installatie klaar. Herstart Enigma2..."
killall -9 enigma2 2>/dev/null || true