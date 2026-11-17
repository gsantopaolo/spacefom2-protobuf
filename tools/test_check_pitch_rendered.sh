#!/usr/bin/env sh
# Tests for check_pitch_rendered.sh: sh tools/test_check_pitch_rendered.sh
set -u
cd "$(dirname "$0")"
fails=0

expect() {  # expect <exit code> <description> <changed paths...>
  want=$1; what=$2; shift 2
  printf '%s\n' "$@" | sh check_pitch_rendered.sh >/dev/null 2>&1
  got=$?
  if [ "$got" -eq "$want" ]; then echo "ok   $what"; else echo "FAIL $what (exit $got, want $want)"; fails=1; fi
}

expect 0 "pitch.md unchanged"            README.md
expect 0 "no files changed"              ""
expect 1 "pitch.md alone"                proposal/pitch.md
expect 1 "pitch.md and PDF only"         proposal/pitch.md proposal/pitch.pdf
expect 1 "pitch.md and DOCX only"        proposal/pitch.md proposal/pitch.docx
expect 0 "all three"                     proposal/pitch.md proposal/pitch.pdf proposal/pitch.docx
expect 0 "PDF refreshed alone"           proposal/pitch.pdf
expect 0 "similar path is not pitch.md"  proposal/pitch.md.bak

exit $fails
