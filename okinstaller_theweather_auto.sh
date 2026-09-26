#!/bin/sh
# Auto-installer script for TheWeather Enigma2 Plugin
# Repository: https://github.com/Caught/TheWeather

TMP_DIR="/tmp"
VERSION="5.0.1"

echo "=========================================="
echo "    Installing TheWeather Plugin...       "
echo "=========================================="

# Function to download from main or master branch
download_file() {
    SUBDIR="$1"
    FILE="$2"

    URL_MAIN="https://raw.githubusercontent.com/Caught/TheWeather/main/${SUBDIR}/${FILE}"
    URL_MASTER="https://raw.githubusercontent.com/Caught/TheWeather/master/${SUBDIR}/${FILE}"

    echo "-> Downloading ${FILE}..."
    wget -q "${URL_MAIN}" -O "${TMP_DIR}/${FILE}"

    # Fallback to master branch if main returned empty/failed
    if [ ! -s "${TMP_DIR}/${FILE}" ]; then
        wget -q "${URL_MASTER}" -O "${TMP_DIR}/${FILE}"
    fi
}

# Try to install a package file, checking OPKG (IPK) first, then DPKG (DEB) if applicable.
try_install() {
    PKG_PATH="$1"
    PKG_NAME="$2"

    # 1. Standard OPKG systems (OpenATV, OpenPLi, OpenBH, OpenViX, etc.)
    if command -v opkg >/dev/null 2>&1; then
        echo "-> Trying: opkg install --force-overwrite --force-reinstall ${PKG_PATH}"
        opkg install --force-overwrite --force-reinstall "${PKG_PATH}" >/tmp/theweather_install.log 2>&1
        
        if opkg list-installed 2>/dev/null | grep -q "^${PKG_NAME} "; then
            return 0
        fi
    fi

    # 2. DreamOS / DPKG systems (Newer Dreamboxes using APT/DPKG)
    # Only run this if apt-get/dpkg is explicitly present to avoid fake .deb errors on OPKG boxes
    if command -v dpkg >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
        DEB_PATH="${PKG_PATH%.ipk}.deb"
        cp "${PKG_PATH}" "${DEB_PATH}" 2>/dev/null

        echo "-> Trying: dpkg -i ${DEB_PATH}"
        dpkg -i "${DEB_PATH}" >/tmp/theweather_install.log 2>&1
        
        # Fix missing dependencies if needed
        apt-get install -f -y >/dev/null 2>&1

        if dpkg -l 2>/dev/null | awk '{print $2}' | grep -q "^${PKG_NAME}$"; then
            rm -f "${DEB_PATH}"
            return 0
        fi
        rm -f "${DEB_PATH}"
    fi

    return 1
}

# 1. Detect package manager and install plugin
if command -v opkg >/dev/null 2>&1 || command -v dpkg >/dev/null 2>&1; then
    PACKAGE_NAME="enigma2-plugin-extensions-theweather"
    PACKAGE_FILE="${PACKAGE_NAME}_${VERSION}_all.ipk"

    cd "${TMP_DIR}" || exit 1
    rm -f "${PACKAGE_NAME}"_*.ipk "${PACKAGE_NAME}"_*.deb

    download_file "ipk" "${PACKAGE_FILE}"

    if [ -s "${TMP_DIR}/${PACKAGE_FILE}" ]; then
        echo "-> Installing package..."
        if try_install "${TMP_DIR}/${PACKAGE_FILE}" "${PACKAGE_NAME}"; then
            echo "-> Installation completed successfully!"
        else
            echo "-> ERROR: installation failed. Last attempt's log:"
            cat /tmp/theweather_install.log 2>/dev/null
            rm -f "${TMP_DIR}/${PACKAGE_FILE}"
            exit 1
        fi
        rm -f "${TMP_DIR}/${PACKAGE_FILE}"
    else
        echo "-> ERROR: Could not download ${PACKAGE_FILE} from GitHub."
        rm -f "${TMP_DIR}/${PACKAGE_FILE}"
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