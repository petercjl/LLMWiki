#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VALIDATOR="$SCRIPT_DIR/validate_ingest_contract.py"

if [[ ! -f "$VALIDATOR" ]]; then
  echo "ERROR: bundled validator not found: $VALIDATOR" >&2
  exit 2
fi

PYTHON_EXECUTABLE=""
for candidate in python3 python; do
  resolved="$(command -v "$candidate" 2>/dev/null || true)"
  [[ -n "$resolved" ]] || continue
  probe="$($resolved -c 'import json, sys; print(json.dumps({"executable": sys.executable, "version": list(sys.version_info[:3])}))' 2>/dev/null || true)"
  if [[ -n "$probe" ]]; then
    PYTHON_EXECUTABLE="$resolved"
    break
  fi
done

if [[ -z "$PYTHON_EXECUTABLE" ]]; then
  echo "ERROR: no working Python interpreter was found on this computer. Repair the Wiki tool environment before claiming ingest success." >&2
  exit 2
fi

python_info="$($PYTHON_EXECUTABLE -c 'import sys; print(f"{sys.executable} ({sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})")')"
echo "Validated Python: $python_info"
exec "$PYTHON_EXECUTABLE" "$VALIDATOR" "$@"
