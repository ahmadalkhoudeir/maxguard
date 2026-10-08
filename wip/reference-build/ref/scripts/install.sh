#!/usr/bin/env bash
# Install MaxGuard from the offline bundle (Jonattan, JON-05).
#
# Run this on the machine WITHOUT internet, inside the folder that holds all
# the bundle files (the parts, compose.yaml and SHA256SUMS):
#
#   bash install.sh
#
# Order matters: every file is checked against SHA256SUMS BEFORE anything is
# loaded, so a damaged or swapped file is caught before it can run.
#
# Settings (environment variables; the defaults install the real bundle):
#   MG_IMAGE             MaxGuard image in the bundle (maxguard:2.0.0a0); it
#                        also unpacks the model volume, because it has tar
#   MODEL_VOLUME         the volume for the AI model (maxguard-ollama-models)
#   MAXGUARD_SKIP_START  1 = load everything but do not run "docker compose up"
#                        (used to test the bundle with small stand-in images)
set -euo pipefail

MG_IMAGE="${MG_IMAGE:-maxguard:2.0.0a0}"
MODEL_VOLUME="${MODEL_VOLUME:-maxguard-ollama-models}"
MAXGUARD_SKIP_START="${MAXGUARD_SKIP_START:-0}"
DASHBOARD_URL="http://127.0.0.1:8000"

die() {
    echo "ERROR: $*" >&2
    exit 1
}

# Linux has sha256sum; macOS has shasum. Both read the same file format.
sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$@"
    else
        shasum -a 256 "$@"
    fi
}

check_tools() {
    command -v docker >/dev/null 2>&1 || die "docker is not installed"
    docker compose version >/dev/null 2>&1 || die "the docker compose plugin is missing"
    docker info >/dev/null 2>&1 || die "Docker is not running: start Docker and try again"
}

verify_checksums() {
    [ -f SHA256SUMS ] || die "SHA256SUMS is missing: copy every bundle file into this folder"
    echo "Checking the SHA-256 checksum of every file..."
    # --strict: a badly formatted line is an error. Without it sha256sum only
    # warns, skips the line and still says everything is fine.
    if ! sha256 -c --strict SHA256SUMS; then
        die "a file is damaged or was changed. Nothing was installed. Download the bundle again."
    fi
}

# Put the files that make up one bundle file into the array PARTS: the whole
# file, or its parts in order (aa, ab, ...; the shell sorts the names). An
# array keeps every file name in one piece, even one with a space in it.
find_parts() {
    local name="$1"
    PARTS=()
    if [ -f "$name" ]; then
        PARTS=("$name")
        return 0
    fi
    local part
    for part in "$name".part-*; do
        if [ -f "$part" ]; then
            PARTS+=("$part")
        fi
    done
    [ "${#PARTS[@]}" -gt 0 ] || die "$name is missing from this folder"
}

# sha256sum -c only checks the files that SHA256SUMS lists, so an extra file
# (for example an added images.tar.part-zz) would pass unnoticed. Refuse any
# file we are about to use that SHA256SUMS does not list.
require_listed() {
    find_parts "$1"
    # Each line is "<64 hex digits><2 characters><file name>": keep the names.
    local listed
    listed="$(cut -c 67- SHA256SUMS)"
    local file
    for file in "${PARTS[@]}"; do
        # <<< instead of a pipe: with pipefail, "cut | grep -q" can fail by
        # chance when grep stops reading early.
        grep -Fxq -- "$file" <<<"$listed" ||
            die "$file is not listed in SHA256SUMS. Nothing was installed."
    done
}

# Print a bundle file to stdout, joining its parts in order (aa, ab, ...).
# Streaming means the joined file never needs extra disk space.
stream_bundle_file() {
    find_parts "$1"
    cat "${PARTS[@]}"
}

load_images() {
    echo "Loading the images (this takes a few minutes)..."
    stream_bundle_file images.tar | docker load
}

# Unpack the model files into the volume Ollama reads, before the first start.
restore_models() {
    echo "Restoring the AI model into the volume $MODEL_VOLUME..."
    docker volume create "$MODEL_VOLUME" >/dev/null
    stream_bundle_file models.tar.gz |
        docker run --rm -i --network none --user 0:0 -v "$MODEL_VOLUME":/models \
            --entrypoint tar "$MG_IMAGE" -xzf - -C /models
}

start_maxguard() {
    if [ "$MAXGUARD_SKIP_START" = "1" ]; then
        echo "MAXGUARD_SKIP_START=1: not starting MaxGuard."
        return
    fi
    # --pull never: everything must come from the bundle; never download.
    docker compose -f compose.yaml up -d --pull never
    echo
    echo "MaxGuard is running. Open the dashboard: $DASHBOARD_URL"
}

main() {
    # Work in the folder that holds this script and the bundle files.
    cd "$(dirname "$0")"
    check_tools
    verify_checksums
    require_listed images.tar
    require_listed models.tar.gz
    require_listed compose.yaml
    load_images
    restore_models
    start_maxguard
}

main "$@"
