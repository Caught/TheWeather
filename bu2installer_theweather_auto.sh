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
    TARGET="${TMP_DIR}/${FILE}"
    
    URL_MAIN="https://raw.githubusercontent.com/Caught/TheWeather/main/${SUBDIR}/${FILE}"
    URL_MASTER="https://raw.githubusercontent.com/Caught/TheWeather/master/${SUBDIR}/${FILE}"
    
    echo "-> Downloading ${FILE}..."
    rm -f "${TARGET}"
    
    wget -q --no-check-certificate "${URL_MAIN}" -O "${TARGET}"
    
    if [ ! -s "${TARGET}" ]; then
        rm -f "${TARGET}"
        wget -q --no-check-certificate "${URL_MASTER}" -O "${TARGET}"
    fi

    if [ ! -s "${TARGET}" ]; then
        rm -f "${TARGET}"
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
        INSTALL_SUCCESS=1
    else
        echo "-> ERROR: Could not download ${PACKAGE_FILE} from GitHub."
        echo "-> Please verify that the file exists in the repository under /ipk/"
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
        INSTALL_SUCCESS=1
    else
        echo "-> ERROR: Could not download ${PACKAGE_FILE} from GitHub."
        echo "-> Please verify that the file exists in the repository under /deb/"
        rm -f ${TMP_DIR}/${PACKAGE_FILE}
        exit 1
    fi
else
    echo "-> ERROR: No supported package manager (opkg/dpkg) found on this system."
    exit 1
fi

if [ "$INSTALL_SUCCESS" = "1" ]; then
    echo "=========================================="
    printf "Do you want to restart the GUI (Enigma2) now? [y/N]: "
    read RESTART < /dev/tty

    case "$RESTART" in 
      y|Y|yes|YES ) 
        echo "-> Restarting GUI now..."
        if command -v systemctl >/dev/null 2>&1; then
            systemctl restart enigma2
        elif command -v init >/dev/null 2>&1; then
            init 4 && init 3
        else
            wget -q -O - http://127.0.0.1/web/powerstate?newstate=3 >/dev/null 2>&1
        fi
        ;;
      * ) 
        echo "-> Restart skipped. Please remember to restart the GUI manually!"
        ;;
    esac
fi

exit 0