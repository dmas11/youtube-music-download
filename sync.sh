#!/bin/bash
# One-click script to sync your YouTube Music library

# Add local node to path if it exists (common on systems using NVM)
if [ -d "$HOME/.nvm/versions/node" ]; then
    NODE_BIN=$(find "$HOME/.nvm/versions/node" -maxdepth 2 -type d -name "bin" | head -n 1)
    [ -n "$NODE_BIN" ] && export PATH="$NODE_BIN:$PATH"
fi

# Run the manager
python3 "$(dirname "$0")/ytm_sync.py" "$@"
