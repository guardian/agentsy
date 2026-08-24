# TUI style guide

Note: This style guide is implemented in [`scripts/lib/terminal-style.sh`](scripts/lib/terminal-style.sh).

Use colour to make output easier to scan, not to carry meaning on its own. Keep messages readable when styling is
disabled and use short labels such as
`Error:` or `Starting:` to identify status.

| Content                           | Style                                |
|-----------------------------------|--------------------------------------|
| Filenames and paths               | Cyan                                 |
| Commands                          | Bold cyan                            |
| Options and environment variables | Yellow                               |
| Status titles                     | Bold, with the semantic colour below |
| Status messages                   | Default terminal colour              |
| Inline code and values            | Cyan                                 |
| Section headings                  | Bold                                 |
| Dividing lines                    | Dim                                  |
| Secondary detail                  | Dim                                  |

Status colours are green for success, blue for information or progress, yellow for warnings, and red for errors. Use a
status title followed by the detail, for example `Error: OPENAI_API_KEY is not set`.

Prefer whitespace and section headings to dividing lines. When a line is helpful, use a short run of ASCII hyphens
rather than terminal-width output.

## Shell scripts

- Emit normal output on standard output and errors on standard error.
- Use `printf` rather than `echo` for styled output.
- Add colour only when the destination is an interactive terminal.
- Disable styling when `NO_COLOR` is non-empty or `TERM` is `dumb`.
- Use the basic ANSI palette so output works across common terminals.
- Reset styling after every styled span so it does not leak into later output.

Source `scripts/lib/terminal-style.sh` rather than adding ANSI codes directly to a script. It exposes these formatting
functions:

| Function                        | Content                                    |
|---------------------------------|--------------------------------------------|
| `terminal_style_filename`       | Filenames and paths                        |
| `terminal_style_command`        | Commands                                   |
| `terminal_style_option`         | Options and environment variables          |
| `terminal_style_status_title`   | Status titles; accepts a status first      |
| `terminal_style_status_message` | Status message text                        |
| `terminal_style_code`           | Inline code and values                     |
| `terminal_style_heading`        | Section headings                           |
| `terminal_style_divider`        | A dividing line; accepts an optional width |
| `terminal_style_detail`         | Secondary detail                           |

The supported statuses are `success`, `info`, `progress`, `warning`, and
`error`. Formatting functions write to standard output without a trailing newline, so callers can compose them with
`printf`. They detect whether their current output destination is a terminal.
