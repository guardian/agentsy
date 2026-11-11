#!/usr/bin/env bash

# Plugin helpers use the caller's error, success and terminal-style functions.

register_marketplace() {
  local dependency marketplaces sources

  for dependency in copilot jq; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
      error "Could not find the '$dependency' command on PATH. Install it before running agentsy install."
      return 1
    fi
  done

  if ! marketplaces=$(copilot plugin marketplace list --json); then
    error "Could not list Copilot plugin marketplaces."
    return 1
  fi
  if ! sources=$(jq -c '[.[] | select(.name == "agentsy") | .source]' <<<"$marketplaces"); then
    error "Could not read Copilot plugin marketplace registrations."
    return 1
  fi

  case "$sources" in
    '[]')
      terminal_style_status_title progress "Registering:"
      printf ' guardian/agentsy marketplace\n'
      if ! copilot plugin marketplace add guardian/agentsy; then
        error "Could not register the guardian/agentsy marketplace."
        return 1
      fi
      success "Registered:" "guardian/agentsy marketplace"
      ;;
    '["GitHub: guardian/agentsy"]')
      success "Ready:" "guardian/agentsy marketplace is already registered"
      ;;
    *)
      error "Marketplace 'agentsy' has conflicting registration: $sources. Expected GitHub: guardian/agentsy; resolve the conflict before retrying."
      return 1
      ;;
  esac
}
