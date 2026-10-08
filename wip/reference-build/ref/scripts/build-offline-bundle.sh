#!/usr/bin/env bash
# Build the MaxGuard offline bundle (Jonattan, JON-05).
#
# Run this on a machine WITH internet, from the repository root:
#
#   scripts/build-offline-bundle.sh
#
# It writes into dist/ everything a machine WITHOUT internet needs:
#   images.tar          the MaxGuard and Ollama images (docker save)
#   models.tar.gz       the files of the model volume (the AI model)
#   compose.yaml        docker/compose.yaml
#   install.sh          scripts/install.sh
#   uninstall.sh        scripts/uninstall.sh
#   OFFLINE-INSTALL.md  the instructions for the user
#   sample-*            three synthetic lab samples for the acceptance test
#   SHA256SUMS          the SHA-256 checksum of every file above
# Any file bigger than PART_BYTES is split into parts (images.tar.part-aa,
# images.tar.part-ab, ...) so each one fits GitHub's 2 GiB limit for release
# files and a FAT32 USB stick (4 GiB limit per file).
#
# Settings (environment variables; the defaults build the real bundle):
#   MG_IMAGE          MaxGuard image; must match docker/compose.yaml (maxguard:2.0.0a0)
#   OLLAMA_IMAGE      Ollama image (ollama/ollama:0.35.1)
#   MAXGUARD_MODEL    the model to pull (qwen3:4b until Ali's evaluation picks the default)
#   MODEL_VOLUME      the Docker volume that holds the models (maxguard-ollama-models)
#   MODEL_SOURCE_DIR  if set, fill MODEL_VOLUME from this folder instead of pulling
#                     a model (used to test the bundle with a small fake model)
#   OFFLINE_DOC       the user instructions to ship (docs/OFFLINE-INSTALL.md)
#   DIST_DIR          where to write the bundle (dist)
#   PART_BYTES        split files bigger than this (1992294400 bytes = 1900 MiB)
#   BUNDLE_PLATFORM   the platform to save (default: this machine's, e.g. linux/amd64)
#
# A bundle holds the images for ONE platform: build one bundle per platform.
# Needs Docker Engine 28 or newer (docker save --platform).
set -euo pipefail

MG_IMAGE="${MG_IMAGE:-maxguard:2.0.0a0}"
OLLAMA_IMAGE="${OLLAMA_IMAGE:-ollama/ollama:0.35.1}"
MAXGUARD_MODEL="${MAXGUARD_MODEL:-qwen3:4b}"
MODEL_VOLUME="${MODEL_VOLUME:-maxguard-ollama-models}"
MODEL_SOURCE_DIR="${MODEL_SOURCE_DIR:-}"
OFFLINE_DOC="${OFFLINE_DOC:-docs/OFFLINE-INSTALL.md}"
DIST_DIR="${DIST_DIR:-dist}"
PART_BYTES="${PART_BYTES:-1992294400}"
BUNDLE_PLATFORM="${BUNDLE_PLATFORM:-}"

# Synthetic lab data (tests/pcaps/, tests/fixtures/), so a tester with no
# internet has something to upload: never a real capture (CLAUDE.md rule 6).
SAMPLES="tests/pcaps/telnet.pcap tests/pcaps/clean_tls13.pcap tests/fixtures/zeek/telnet"

# A short-lived Ollama container that downloads the model into the volume.
PULL_CONTAINER="maxguard-bundle-ollama"

die() {
    echo "ERROR: $*" >&2
    exit 1
}

# Linux has sha256sum; macOS has shasum. Both write the same file format.
sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$@"
    else
        shasum -a 256 "$@"
    fi
}

check_inputs() {
    command -v docker >/dev/null 2>&1 || die "docker is not installed"
    [ -f docker/compose.yaml ] || die "run this script from the repository root"
    [ -f "$OFFLINE_DOC" ] || die "missing $OFFLINE_DOC"
    for sample in $SAMPLES; do
        [ -e "$sample" ] || die "missing $sample"
    done
    if [ -n "$MODEL_SOURCE_DIR" ] && [ ! -d "$MODEL_SOURCE_DIR" ]; then
        die "MODEL_SOURCE_DIR $MODEL_SOURCE_DIR is not a folder"
    fi
    # Old parts left in dist/ would end up in SHA256SUMS and be joined into
    # the new images, so refuse to mix two builds.
    if [ -d "$DIST_DIR" ] && [ -n "$(ls -A "$DIST_DIR")" ]; then
        die "$DIST_DIR is not empty: move or delete it first (rm -r $DIST_DIR)"
    fi
    mkdir -p "$DIST_DIR"
    if [ -z "$BUNDLE_PLATFORM" ]; then
        BUNDLE_PLATFORM="$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')"
    fi
    echo "Building a bundle for $BUNDLE_PLATFORM"
}

# Use the MaxGuard image if this machine has it, otherwise build it.
ensure_maxguard_image() {
    if docker image inspect "$MG_IMAGE" >/dev/null 2>&1; then
        echo "Using the image $MG_IMAGE that is already on this machine"
    else
        echo "Building $MG_IMAGE from docker/Dockerfile"
        # --target runtime: the same stage the release workflow builds (the
        # Dockerfile also has a "test" stage).
        docker build -f docker/Dockerfile --target runtime -t "$MG_IMAGE" .
    fi
}

ensure_ollama_image() {
    if docker image inspect "$OLLAMA_IMAGE" >/dev/null 2>&1; then
        echo "Using the image $OLLAMA_IMAGE that is already on this machine"
    else
        docker pull --platform "$BUNDLE_PLATFORM" "$OLLAMA_IMAGE"
    fi
}

remove_pull_container() {
    docker rm -f "$PULL_CONTAINER" >/dev/null 2>&1 || true
}

# Start a temporary Ollama server on the model volume and ask it to pull the model.
pull_model_into_volume() {
    echo "Pulling the model $MAXGUARD_MODEL into the volume $MODEL_VOLUME"
    remove_pull_container
    trap remove_pull_container EXIT
    docker run -d --name "$PULL_CONTAINER" -v "$MODEL_VOLUME":/root/.ollama "$OLLAMA_IMAGE" >/dev/null
    # The server needs a moment to start; "ollama list" works once it answers.
    local tries=0
    until docker exec "$PULL_CONTAINER" ollama list >/dev/null 2>&1; do
        tries=$((tries + 1))
        [ "$tries" -le 30 ] || die "the temporary Ollama server did not start"
        sleep 1
    done
    docker exec "$PULL_CONTAINER" ollama pull "$MAXGUARD_MODEL"
    echo "Models now in the volume (all of them go into the bundle):"
    docker exec "$PULL_CONTAINER" ollama list
    remove_pull_container
}

# Tests use a small fake model folder instead of downloading gigabytes.
copy_model_folder_into_volume() {
    echo "Filling the volume $MODEL_VOLUME from $MODEL_SOURCE_DIR (no model pull)"
    # tar streams through stdin, so nothing is bind-mounted and every file in
    # the volume is written by the container (no root-owned files on the host).
    tar -C "$MODEL_SOURCE_DIR" -cf - . |
        docker run --rm -i --network none --user 0:0 -v "$MODEL_VOLUME":/models \
            --entrypoint tar "$MG_IMAGE" -xf - -C /models
}

save_images() {
    echo "Saving $MG_IMAGE and $OLLAMA_IMAGE ($BUNDLE_PLATFORM) to $DIST_DIR/images.tar"
    # --platform: with Docker's containerd image store an image can hold
    # several platforms; the bundle must carry exactly the one it is for.
    docker save --platform "$BUNDLE_PLATFORM" -o "$DIST_DIR/images.tar" "$MG_IMAGE" "$OLLAMA_IMAGE"
}

# The MaxGuard image has tar; the volume is read-only and the archive is
# written to stdout, so the file on the host belongs to you, not to root.
save_model_volume() {
    echo "Saving the volume $MODEL_VOLUME to $DIST_DIR/models.tar.gz"
    docker run --rm --network none --user 0:0 -v "$MODEL_VOLUME":/models:ro \
        --entrypoint tar "$MG_IMAGE" -czf - -C /models . >"$DIST_DIR/models.tar.gz"
}

copy_small_files() {
    cp docker/compose.yaml "$DIST_DIR/compose.yaml"
    cp scripts/install.sh "$DIST_DIR/install.sh"
    cp scripts/uninstall.sh "$DIST_DIR/uninstall.sh"
    cp "$OFFLINE_DOC" "$DIST_DIR/OFFLINE-INSTALL.md"
    chmod +x "$DIST_DIR/install.sh" "$DIST_DIR/uninstall.sh"
    cp tests/pcaps/telnet.pcap "$DIST_DIR/sample-telnet.pcap"
    cp tests/pcaps/clean_tls13.pcap "$DIST_DIR/sample-clean-tls13.pcap"
    tar -czf "$DIST_DIR/sample-telnet-zeek-logs.tar.gz" -C tests/fixtures/zeek telnet
}

# Split a file into numbered parts if it is bigger than PART_BYTES.
split_if_big() {
    local file="$1"
    local size
    size="$(wc -c <"$file" | tr -d ' ')"
    if [ "$size" -gt "$PART_BYTES" ]; then
        echo "Splitting $file ($size bytes) into parts of $PART_BYTES bytes"
        split -b "$PART_BYTES" "$file" "$file.part-"
        rm "$file"
    fi
}

write_checksums() {
    echo "Writing $DIST_DIR/SHA256SUMS"
    # Run inside dist/ so SHA256SUMS holds plain file names, not paths. The
    # sums are computed first, so SHA256SUMS never lists itself.
    (
        cd "$DIST_DIR"
        local sums
        sums="$(sha256 -- *)"
        printf '%s\n' "$sums" >SHA256SUMS
    )
}

main() {
    check_inputs
    ensure_maxguard_image
    ensure_ollama_image
    if [ -n "$MODEL_SOURCE_DIR" ]; then
        copy_model_folder_into_volume
    else
        pull_model_into_volume
    fi
    save_images
    save_model_volume
    copy_small_files
    split_if_big "$DIST_DIR/images.tar"
    split_if_big "$DIST_DIR/models.tar.gz"
    write_checksums
    echo "Done. The bundle is in $DIST_DIR/:"
    ls -l "$DIST_DIR"
}

main "$@"
