#!/usr/bin/env bash

# Terminal formatting helpers. Public functions use the terminal_style_ prefix;
# underscored functions are internal to this module.

_terminal_style_enabled() {
  [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != "dumb" ]
}

_terminal_style_wrap() {
  local code="$1"
  shift

  if _terminal_style_enabled; then
    printf '\033[%sm' "$code" # ESC starts an ANSI SGR sequence.
    printf '%s' "$@"
    printf '\033[0m' # 0 resets all styles.
  else
    printf '%s' "$@"
  fi
}

terminal_style_filename() {
  # 36 sets the foreground colour to cyan.
  _terminal_style_wrap 36 "$@"
}

terminal_style_command() {
  # 1 enables bold; 36 sets cyan.
  _terminal_style_wrap '1;36' "$@"
}

terminal_style_option() {
  # 33 sets the foreground colour to yellow.
  _terminal_style_wrap 33 "$@"
}

terminal_style_status_title() {
  local status="$1"
  local code
  shift

  case "$status" in
    success)
      code=32 # Green
      ;;
    info | progress)
      code=34 # Blue
      ;;
    warning)
      code=33 # Yellow
      ;;
    error)
      code=31 # Red
      ;;
    *)
      printf 'terminal_style_status_title: unsupported status %q\n' "$status" >&2
      return 2
      ;;
  esac

  # 1 adds bold to the status colour.
  _terminal_style_wrap "1;$code" "$@"
}

terminal_style_status_message() {
  printf '%s' "$@"
}

terminal_style_code() {
  # 36 sets the foreground colour to cyan.
  _terminal_style_wrap 36 "$@"
}

terminal_style_heading() {
  # 1 enables bold.
  _terminal_style_wrap 1 "$@"
}

terminal_style_divider() {
  local width="${1:-40}"
  local line

  if ! [[ "$width" =~ ^[1-9][0-9]*$ ]]; then
    printf 'terminal_style_divider: width must be a positive integer\n' >&2
    return 2
  fi

  printf -v line '%*s' "$width" ''
  # 2 enables dim text.
  _terminal_style_wrap 2 "${line// /-}"
}

terminal_style_detail() {
  # 2 enables dim text.
  _terminal_style_wrap 2 "$@"
}
