#!/bin/sh
set -e

REPO="Caught/TheWeather"
NAME="theweather"
VERSION="4.4"

download_and_check() {
    URL="$1"
    DEST="$2"

    echo "Downloading $(basename "$DEST") ..."
    echo "URL: $URL"
    echo ""

    rm -f "$DEST"

    if ! wget \
        --no-check-certificate \
        --timeout=60 \
        --tries=3 \
        -O "$DEST" \
        "$URL"
    then
        echo ""
        echo "ERROR: download failed:"
        echo "  $URL"
        rm -f "$DEST"
        exit 1
    fi

    SIZE=$(wc -c < "$DEST" 2>/dev/null || echo 0)

    echo ""
    echo "Downloaded size: ${SIZE} bytes"

    if [ "$SIZE" -lt 1000 ]; then
        echo ""
        echo "ERROR: downloaded file is too small:"
        echo "  ${SIZE} bytes"
        echo ""
        echo "The downloaded file is probably invalid."
        rm -f "$DEST"
        exit 1
    fi

    # IPK files are ar archives and must start with !<arch>
    MAGIC=$(dd if="$DEST" bs=1 count=7 2>/dev/null || true)

    if [ "$MAGIC" != "!<arch>" ]; then
        echo ""
        echo "ERROR: downloaded file is NOT a valid IPK archive."
        echo ""
        echo "Expected IPK header:"
        echo "  !<arch>"
        echo ""
        echo "Received:"
        echo "  $MAGIC"
        echo ""
        echo "File:"
        echo "  $DEST"
        echo ""
        echo "Possible causes:"
        echo "  - GitHub returned an error page"
        echo "  - incomplete download"
        echo "  - proxy/cache problem"
        echo "  - invalid package in the repository"
        echo ""

        rm -f "$DEST"
        exit 1
    fi

    echo "IPK archive check: OK"
    echo ""
}


if command -v dpkg >/dev/null 2>&1; then

    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.deb"
    URL="https://raw.githubusercontent.com/${REPO}/main/deb/${PKG}"

    download_and_check "$URL" "/tmp/${PKG}"

    echo "Installing ${PKG} ..."
    dpkg -i "/tmp/${PKG}"

    rm -f "/tmp/${PKG}"

elif command -v opkg >/dev/null 2>&1; then

    PKG="enigma2-plugin-extensions-${NAME}_${VERSION}_all.ipk"
    URL="https://raw.githubusercontent.com/${REPO}/main/ipk/${PKG}"

    download_and_check "$URL" "/tmp/${PKG}"

    echo "Installing ${PKG} ..."

    opkg install \
        --force-reinstall \
        --force-downgrade \
        --force-overwrite \
        "/tmp/${PKG}"

    rm -f "/tmp/${PKG}"

else

    echo ""
    echo "ERROR: No opkg or dpkg found."
    echo "Cannot proceed with installation."
    exit 1

fi


echo ""
echo "======================================================="
echo " Installation of TheWeather v${VERSION} completed!"
echo " Please restart Enigma2 (GUI) to activate the plugin."
echo "======================================================="
echo ""