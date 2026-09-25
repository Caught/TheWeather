#!/bin/sh
# Auto-installer script for TheWeather Enigma2 Plugin
# Repository: https://github.com/Caught/TheWeather

TMP_DIR="/tmp"
VERSION="5.0"

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

# Try to install a package file, trying several install methods in turn.
# Some images expose an "opkg" command that is actually a wrapper around
# apt/dpkg rather than real opkg, and those wrappers can reject certain
# flag combinations (e.g. "--force-overwrite --force-reinstall" together)
# or only accept local files with a ".deb" extension. Real opkg, on the
# other hand, does not understand ".deb"-suffixed local files at all.
# So: try the most compatible commands first, without assuming which
# implementation is actually behind "opkg" on this box, and verify the
# result by checking the package database afterwards instead of trusting
# any command's exit code or printed text alone.
try_install() {
    PKG_PATH="$1"
    PKG_NAME="$2"

    # 1. Plain opkg install, no force flags (works on real opkg; also
    #    works on some apt/opkg-wrapper images).
    if command -v opkg >/dev/null 2>&1; then
        echo "-> Trying: opkg install ${PKG_PATH}"
        opkg install "${PKG_PATH}" >/tmp/theweather_install.log 2>&1
        if opkg list-installed 2>/dev/null | grep -q "^${PKG_NAME} "; then
            return 0
        fi
    fi

    # 2. Some opkg wrappers (apt/dpkg-based) only accept local files that
    #    end in ".deb" when passed to "install". If our file is ".ipk",
    #    make a ".deb"-named copy pointing at the same content and retry.
    case "${PKG_PATH}" in
        *.ipk)
            DEB_PATH="${PKG_PATH%.ipk}.deb"
            cp "${PKG_PATH}" "${DEB_PATH}" 2>/dev/null
            if command -v opkg >/dev/null 2>&1; then
                echo "-> Trying: opkg install ${DEB_PATH}"
                opkg install "${DEB_PATH}" >/tmp/theweather_install.log 2>&1
                if opkg list-installed 2>/dev/null | grep -q "^${PKG_NAME} "; then
                    rm -f "${DEB_PATH}"
                    return 0
                fi
            fi
            ;;
        *)
            DEB_PATH=""
            ;;
    esac

    # 3. Fall back to dpkg directly, if present. This is what actually
    #    works on boxes where "opkg" turned out to be an apt/dpkg wrapper
    #    that does not support installing local files via "install" at all.
    if command -v dpkg >/dev/null 2>&1; then
        TARGET="${DEB_PATH:-$PKG_PATH}"
        echo "-> Trying: dpkg -i ${TARGET}"
        dpkg -i "${TARGET}" >/tmp/theweather_install.log 2>&1
        if dpkg -l 2>/dev/null | awk '{print $2}' | grep -q "^${PKG_NAME}$"; then
            [ -n "${DEB_PATH}" ] && rm -f "${DEB_PATH}"
            return 0
        fi
    fi

    [ -n "${DEB_PATH}" ] && rm -f "${DEB_PATH}"
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