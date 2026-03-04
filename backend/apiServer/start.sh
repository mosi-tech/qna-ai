#!/bin/bash
if [ "$TRACK_CALLS" = "true" ]; then
  eval "$(curl -sS localhost:8001/setup 2>/dev/null)" || true
fi
exec python3 server.py
