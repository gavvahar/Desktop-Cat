#!/bin/sh
export PYTHONPATH="/app/share/desktopcat:${PYTHONPATH}"
exec python3 -m desktopcat.main "$@"
