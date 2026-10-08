#!/usr/bin/env bash
# Remove MaxGuard from this machine (Jonattan, JON-05).
#
#   bash uninstall.sh          stop MaxGuard, then ASK before deleting its data
#   bash uninstall.sh --yes    stop MaxGuard and delete its data without asking
#
# Stopping removes the containers and networks. The volumes hold your alerts,
# reports, audit log (maxguard-data) and the AI model (maxguard-ollama-models);
# they are deleted only after you type "yes" (or with --yes), because that
# cannot be undone. The images stay; the script prints how to remove them.
#
# Settings (environment variables, used by the tests):
#   COMPOSE_PROJECT_NAME  the Compose project to stop (maxguard)
#   DATA_VOLUME           the data volume (maxguard-data)
#   MODEL_VOLUME          the model volume (maxguard-ollama-models)
set -euo pipefail

PROJECT="${COMPOSE_PROJECT_NAME:-maxguard}"
DATA_VOLUME="${DATA_VOLUME:-maxguard-data}"
MODEL_VOLUME="${MODEL_VOLUME:-maxguard-ollama-models}"

usage() {
    echo "usage: bash uninstall.sh [--yes]" >&2
    exit 2
}

# --yes is for scripts and tests; without it a person must confirm.
parse_args() {
    ASSUME_YES=0
    if [ "$#" -gt 1 ]; then
        usage
    fi
    if [ "$#" -eq 1 ]; then
        [ "$1" = "--yes" ] || usage
        ASSUME_YES=1
    fi
}

stop_maxguard() {
    echo "Stopping MaxGuard (project $PROJECT)..."
    # Compose finds the containers by project name, so no compose file is needed.
    docker compose -p "$PROJECT" down
}

# Anything except a typed "yes" keeps the data, including an empty answer or
# no keyboard at all (for example when the script runs from cron).
confirm_delete() {
    if [ "$ASSUME_YES" = "1" ]; then
        return 0
    fi
    local answer=""
    echo "Delete the volumes $DATA_VOLUME and $MODEL_VOLUME?"
    echo "This deletes all alerts, reports, the audit log and the AI model. It cannot be undone."
    printf 'Type yes to delete them: '
    read -r answer || answer=""
    [ "$answer" = "yes" ]
}

remove_volume() {
    local volume="$1"
    if docker volume inspect "$volume" >/dev/null 2>&1; then
        docker volume rm "$volume" >/dev/null
        echo "Deleted the volume $volume"
    else
        echo "The volume $volume does not exist"
    fi
}

main() {
    parse_args "$@"
    command -v docker >/dev/null 2>&1 || {
        echo "ERROR: docker is not installed" >&2
        exit 1
    }
    stop_maxguard
    if confirm_delete; then
        remove_volume "$DATA_VOLUME"
        remove_volume "$MODEL_VOLUME"
    else
        echo
        echo "Kept the volumes $DATA_VOLUME and $MODEL_VOLUME."
    fi
    echo "The images are still on this machine. To remove them too:"
    echo "  docker image rm maxguard:2.0.0a0 ollama/ollama:0.35.1"
}

main "$@"
