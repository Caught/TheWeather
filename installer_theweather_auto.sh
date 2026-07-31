#!/bin/sh
set -e

REPO="Caught/TheWeather"
NAME="theweather"
VERSION="3.0"
TAG="v${VERSION}"

if command -v dpkg >/dev/null 2>&1; then
    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.deb"
    URL="https://github.com/${REPO}/releases/download/${TAG}/${PKG}"
    echo "Downloading $PKG ..."
    wget -q -O "/tmp/${PKG}" "$URL"
    dpkg -i "/tmp/${PKG}"
elif command -v opkg >/dev/null 2>&1; then
    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.ipk"
    URL="https://raw.githubusercontent.com/${REPO}/main/ipk/${PKG}"
    echo "Downloading $PKG ..."
    wget -q -O "/tmp/${PKG}" "$URL"
    opkg install "/tmp/${PKG}"
else
    echo "Geen opkg of dpkg gevonden — kan niet installeren."
    exit 1
fi

echo "Installatie klaar. Herstart Enigma2..."
killall -9 enigma2 2>/dev/null || true
