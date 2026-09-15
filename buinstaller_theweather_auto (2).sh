#!/bin/sh

PLUGIN_SOURCE="/tmp/plugin_build"
PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather"
BACKUPPATH="/tmp/TheWeather_backup"

log() {
    echo "[INFO] $1"
}

error() {
    echo "[ERROR] $1" >&2
}

remove_repository_only_files()
{
    log "Removing repository-only files and directories..."

    rm -f "$PLUGIN_SOURCE/README.md"
    rm -f "$PLUGIN_SOURCE/installer.sh"
    rm -f "$PLUGIN_SOURCE/version.txt"

    find "$PLUGIN_SOURCE" -type f -name "*.svg" -exec rm -f {} + 2>/dev/null || true

    if [ -d "$PLUGIN_SOURCE/converter" ]; then
        rm -rf "$PLUGIN_SOURCE/converter"
        log "Converter folder removed from source."
    fi

    if [ -d "$PLUGIN_SOURCE/renderer" ]; then
        rm -rf "$PLUGIN_SOURCE/renderer"
        log "Renderer folder removed from source."
    fi

    log "Repository-only files and directories removed."
}

rollback_plugin() {
    log "Rolling back installation..."
    if [ -d "$BACKUPPATH" ]; then
        rm -rf "$PLUGINPATH"
        mv "$BACKUPPATH" "$PLUGINPATH"
        log "Backup restored."
    else
        error "No backup found to restore!"
    fi
}

cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$PLUGIN_SOURCE"
    rm -rf "$BACKUPPATH"
}

install_plugin() {
    log "Starting installation..."

    if [ -d "$PLUGINPATH" ]; then
        log "Backing up existing installation..."
        rm -rf "$BACKUPPATH"
        cp -a "$PLUGINPATH" "$BACKUPPATH"
    fi

    remove_repository_only_files

    mkdir -p "$PLUGINPATH"
    if cp -a "$PLUGIN_SOURCE"/. "$PLUGINPATH"/; then
        log "Plugin files copied successfully."
    else
        error "Failed to copy plugin files."
        rollback_plugin
        cleanup
        exit 1
    fi

    if [ -f "$PLUGINPATH/README.md" ] || [ -f "$PLUGINPATH/installer.sh" ] || [ -f "$PLUGINPATH/version.txt" ]; then
        error "Installation verification failed: Repository files were found in target folder."
        rollback_plugin
        cleanup
        exit 1
    fi

    if [ "$(find "$PLUGINPATH" -type f -name "*.svg" | wc -l)" -gt 0 ]; then
        error "Installation verification failed: .svg files were found in target folder."
        rollback_plugin
        cleanup
        exit 1
    fi

    log "Verification passed successfully."
    cleanup
}

restart_gui_prompt() {
    if [ -t 0 ] || [ -e /dev/tty ]; then
        printf "Do you want to restart the Enigma2 GUI now? (y/n): "
        read -r RESTART < /dev/tty
        case "$RESTART" in
            [Yy]*)
                log "Restarting Enigma2 GUI..."
                init 4 && init 3
                ;;
            *)
                log "GUI restart skipped. Please restart Enigma2 manually."
                ;;
        esac
    else
        log "Non-interactive session detected. Skipping GUI restart prompt."
    fi
}

install_plugin
restart_gui_prompt