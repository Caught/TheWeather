#!/bin/sh
# Auto-installer script for TheWeather Enigma2 Plugin
# Repository: https://github.com/Caught/TheWeather

TMP_DIR="/tmp"
VERSION="4.5"

echo "=========================================="
echo "    Installing TheWeather Plugin...       "
echo "=========================================="


download_file() {
    SUBDIR="$1"
    FILE="$2"
    
    URL_MAIN="https://raw.githubusercontent.com/Caught/TheWeather/main/${SUBDIR}/${FILE}"
    URL_MASTER="https://raw.githubusercontent.com/Caught/TheWeather/master/${SUBDIR}/${FILE}"
    
    echo "-> Downloading ${FILE}..."
    wget -q "${URL_MAIN}" -O "${TMP_DIR}/${FILE}"
    
    if [ ! -s "${TMP_DIR}/${FILE}" ]; then
        wget -q "${URL_MASTER}" -O "${TMP_DIR}/${FILE}"
    fi
}

if command -v opkg >/dev/null 2>&1; then
    echo "-> OPKG package manager detected (IPK system)..."
    PACKAGE_FILE="enigma2-plugin-extensions-theweather_${VERSION}_all.ipk"
    
    cd ${TMP_DIR}
    rm -f enigma2-plugin-extensions-theweather_*.ipk
    
    download_file "ipk" "${PACKAGE_FILE}"
    
    if [ -s "${TMP_DIR}/${PACKAGE_FILE}" ]; then
        echo "-> Installing package..."
        opkg install --force-overwrite --force-reinstall ${TMP_DIR}/${PACKAGE_FILE}
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        echo "-> Installation completed successfully!"
    else
        echo "-> ERROR: Could not download ${PACKAGE_FILE} from GitHub."
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        exit 1
    fi

elif command -v dpkg >/dev/null 2>&1; then
    echo "-> DPKG package manager detected (DEB system / DreamOS)..."
    PACKAGE_FILE="enigma2-plugin-extensions-theweather_${VERSION}_all.deb"
    
    cd ${TMP_DIR}
    rm -f enigma2-plugin-extensions-theweather_*.deb
    
    download_file "deb" "${PACKAGE_FILE}"
    
    if [ -s "${TMP_DIR}/${PACKAGE_FILE}" ]; then
        echo "-> Installing package..."
        dpkg -i ${TMP_DIR}/${PACKAGE_FILE}
        apt-get install -f -y >/dev/null 2>&1
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        echo "-> Installation completed successfully!"
    else
        echo "-> ERROR: Could not download ${PACKAGE_FILE} from GitHub."
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        exit 1
    fi
else
    echo "-> ERROR: No supported package manager (opkg/dpkg) found on this system."
    exit 1
fi

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