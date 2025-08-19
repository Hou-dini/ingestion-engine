#!/usr/bin/env bash
# Load secrets from environment-friendly secret backends into the current shell session
# and optionally run the coordinator script (no-persist mode).
#
# This script expects the following commands to exist for secret retrieval:
# - `secret-tool` (libsecret) OR
# - `pass` (password-store) OR
# - `gopass` (optional)
#
# It will attempt multiple backends in order of availability. If none are found,
# it will fall back to reading existing environment variables.
#
# Usage:
#   # Load secrets into current shell (source the script):
#   source ./scripts/load_secrets_and_run.sh
#
#   # Load secrets and run the coordinator immediately:
#   source ./scripts/load_secrets_and_run.sh --run
#
# Notes:
# - POSIX shells cannot access secret-management modules on Windows. This script
#   provides a best-effort approach for Linux/macOS devs. For Windows, prefer
#   the PowerShell helper `scripts/load_secrets_and_run.ps1`.

VAULT_NAME=${VAULT_NAME:-LocalStore}
COORDINATOR_SCRIPT=${COORDINATOR_SCRIPT:-./scripts/run_coordinator_no_persist.py}
RUN=0
UNSET_AFTER=0

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --run) RUN=1; shift ;;
    --unset-after) UNSET_AFTER=1; shift ;;
    --vault) VAULT_NAME="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Helper to try multiple secret backends
get_secret() {
  name="$1"
  # try pass
  if command -v pass >/dev/null 2>&1; then
    val=$(pass "${VAULT_NAME}/${name}" 2>/dev/null || true)
    if [[ -n "$val" ]]; then echo "$val"; return; fi
  fi
  # try secret-tool (libsecret)
  if command -v secret-tool >/dev/null 2>&1; then
    val=$(secret-tool lookup "$VAULT_NAME" "$name" 2>/dev/null || true)
    if [[ -n "$val" ]]; then echo "$val"; return; fi
  fi
  # try gopass
  if command -v gopass >/dev/null 2>&1; then
    val=$(gopass show "${VAULT_NAME}/${name}" 2>/dev/null || true)
    if [[ -n "$val" ]]; then echo "$val"; return; fi
  fi
  # fallback to existing env var
  if [[ -n "${!name}" ]]; then
    echo "${!name}"
  fi
}

REDDIT_CLIENT_ID=$(get_secret REDDIT_CLIENT_ID)
REDDIT_CLIENT_SECRET=$(get_secret REDDIT_CLIENT_SECRET)
REDDIT_USER_AGENT=$(get_secret REDDIT_USER_AGENT)
GCS_CREDENTIALS_JSON=$(get_secret GCS_CREDENTIALS_JSON)
GCS_BUCKET_NAME=$(get_secret GCS_BUCKET_NAME)

# Export if set
[[ -n "$REDDIT_CLIENT_ID" ]] && export REDDIT_CLIENT_ID
[[ -n "$REDDIT_CLIENT_SECRET" ]] && export REDDIT_CLIENT_SECRET
[[ -n "$REDDIT_USER_AGENT" ]] && export REDDIT_USER_AGENT
[[ -n "$GCS_CREDENTIALS_JSON" ]] && export GCS_CREDENTIALS_JSON
[[ -n "$GCS_BUCKET_NAME" ]] && export GCS_BUCKET_NAME

redact() {
  v="$1"
  if [[ -z "$v" ]]; then echo ""; return; fi
  len=${#v}
  if [[ $len -le 8 ]]; then echo "REDACTED"; return; fi
  echo "${v:0:4}...${v: -4}"
}

printf "Loaded settings (redacted):\n"
printf "  REDDIT_CLIENT_ID=%s\n" "$(redact "$REDDIT_CLIENT_ID")"
printf "  REDDIT_CLIENT_SECRET=%s\n" "$(redact "$REDDIT_CLIENT_SECRET")"
printf "  REDDIT_USER_AGENT=%s\n" "$REDDIT_USER_AGENT"
printf "  GCS_CREDENTIALS_JSON=%s\n" "$(redact "$GCS_CREDENTIALS_JSON")"
printf "  GCS_BUCKET_NAME=%s\n" "$GCS_BUCKET_NAME"

if [[ $RUN -eq 1 ]]; then
  echo "Running coordinator script: $COORDINATOR_SCRIPT"
  python "$COORDINATOR_SCRIPT"
fi

if [[ $UNSET_AFTER -eq 1 ]]; then
  unset REDDIT_CLIENT_ID REDDIT_CLIENT_SECRET REDDIT_USER_AGENT GCS_CREDENTIALS_JSON GCS_BUCKET_NAME
  echo "Environment variables removed from session."
fi
