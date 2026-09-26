#!/bin/sh
# Auto-installer script for TheWeather Enigma2 Plugin
# Repository: https://github.com/Caught/TheWeather

TMP_DIR="/tmp"
VERSION="5.0.1"

echo "=========================================="
echo "    Installing TheWeather Plugin...       "
echo "=========================================="

# Download a file from the main branch, falling back to master, with
# retries and a size check against the server's Content-Length. This
# guards against silently installing a truncated/partial download
# (the classic symptom is an opkg/dpkg error like:
#   "Truncated input file (needed 4608 bytes, only 0 available)")
download_file() {
    SUBDIR="$1"
    FILE="$2"
    OUT="${TMP_DIR}/${FILE}"
    MAX_TRIES=3

    for BRANCH in main master; do
        URL="https://raw.githubusercontent.com/Caught/TheWeather/${BRANCH}/${SUBDIR}/${FILE}"
        EXPECTED=$(wget -q -S --spider "${URL}" 2>&1 | sed -n 's/^ *Content-Length: *\([0-9]*\).*/\1/p' | tail -1)

        i=1
        while [ "$i" -le "$MAX_TRIES" ]; do
            echo "-> Downloading ${FILE} from ${BRANCH} (attempt ${i}/${MAX_TRIES})..."
            rm -f "${OUT}"
            wget -q -T 30 "${URL}" -O "${OUT}"

            ACTUAL=$(wc -c < "${OUT}" 2>/dev/null)
            ACTUAL=${ACTUAL:-0}

            if [ -n "${EXPECTED}" ] && [ "${ACTUAL}" = "${EXPECTED}" ]; then
                return 0
            elif [ -z "${EXPECTED}" ] && [ "${ACTUAL}" -gt 4608 ] 2>/dev/null; then
                # Could not determine the server-side size (e.g. wget
                # doesn't support --spider on this box) -> fall back to
                # a sane minimum-size heuristic instead.
                return 0
            fi

            echo "-> Download incomplete (got ${ACTUAL} of ${EXPECTED:-unknown} bytes), retrying..."
            i=$((i + 1))
        done
    done

    rm -f "${OUT}"
    return 1
}

# Try to install a package file, trying several install methods in turn.
# Some images expose an "opkg" command that is actually a wrapper around
# apt/dpkg rather than real opkg, and those wrappers can reject certain
# flag combinations or only accept local files with a ".deb" extension.
# Real opkg, on the other hand, does not understand ".deb"-suffixed local
# files at all. So: try the most likely-to-work commands first, without
# assuming which implementation is actually behind "opkg" on this box,
# and verify the result by checking the package database afterwards
# instead of trusting any command's exit code or printed text alone.
try_install() {
    PKG_PATH="$1"
    PKG_NAME="$2"

    # 1. Standard OPKG systems (OpenATV, OpenPLi, OpenBH, OpenViX, etc.)
    #    Use force flags so a stuck/partial previous install gets
    #    properly overwritten instead of being skipped as "already there".
    if command -v opkg >/dev/null 2>&1; then
        echo "-> Trying: opkg install --force-overwrite --force-reinstall ${PKG_PATH}"
        opkg install --force-overwrite --force-reinstall "${PKG_PATH}" >/tmp/theweather_install.log 2>&1
        if opkg list-installed 2>/dev/null | grep -q "^${PKG_NAME} "; then
            return 0
        fi

        # Some opkg wrappers (apt/dpkg-based) reject the force flags
        # together; retry without them before giving up on opkg.
        echo "-> Trying: opkg install ${PKG_PATH} (without force flags)"
        opkg install "${PKG_PATH}" >>/tmp/theweather_install.log 2>&1
        if opkg list-installed 2>/dev/null | grep -q "^${PKG_NAME} "; then
            return 0
        fi
    fi

    # 2. Some opkg wrappers only accept local files that end in ".deb"
    #    when passed to "install". If our file is ".ipk", make a
    #    ".deb"-named copy pointing at the same content and retry.
    case "${PKG_PATH}" in
        *.ipk)
            DEB_PATH="${PKG_PATH%.ipk}.deb"
            cp "${PKG_PATH}" "${DEB_PATH}" 2>/dev/null
            ;;
        *)
            DEB_PATH=""
            ;;
    esac

    if [ -n "${DEB_PATH}" ] && command -v opkg >/dev/null 2>&1; then
        echo "-> Trying: opkg install ${DEB_PATH}"
        opkg install --force-overwrite --force-reinstall "${DEB_PATH}" >>/tmp/theweather_install.log 2>&1
        if opkg list-installed 2>/dev/null | grep -q "^${PKG_NAME} "; then
            rm -f "${DEB_PATH}"
            return 0
        fi
    fi

    # 3. DreamOS/DPKG systems (newer Dreamboxes on APT/DPKG), and any
    #    other box where "opkg" turned out to be a wrapper that couldn't
    #    install a local file via "install" at all. Works even without
    #    apt-get present; if apt-get IS present, use it afterwards to
    #    fix any missing dependencies.
    if command -v dpkg >/dev/null 2>&1; then
        TARGET="${DEB_PATH:-$PKG_PATH}"
        echo "-> Trying: dpkg -i ${TARGET}"
        dpkg -i "${TARGET}" >>/tmp/theweather_install.log 2>&1

        if command -v apt-get >/dev/null 2>&1; then
            apt-get install -f -y >/dev/null 2>&1
        fi

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
        echo "-> ERROR: Could not download a complete ${PACKAGE_FILE} from GitHub."
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
