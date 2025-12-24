#!/bin/bash
# Installation script for JSON comparison tools

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"

echo "JSON Comparison Tools Installer"
echo "================================"
echo ""
echo "This will install the following commands:"
echo "  - jcompare  (compare two JSON files)"
echo "  - jfetch    (fetch JSON from curl commands)"
echo ""
echo "Install location: $INSTALL_DIR"
echo ""

# Make scripts executable
chmod +x "$SCRIPT_DIR/jcompare"
chmod +x "$SCRIPT_DIR/jfetch"

# Check if we need sudo
if [ -w "$INSTALL_DIR" ]; then
    SUDO=""
else
    echo "Note: Installation requires administrator privileges"
    SUDO="sudo"
fi

# Create symlinks
echo "Creating symlinks..."
$SUDO ln -sf "$SCRIPT_DIR/jcompare" "$INSTALL_DIR/jcompare"
$SUDO ln -sf "$SCRIPT_DIR/jfetch" "$INSTALL_DIR/jfetch"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Usage:"
echo "  jcompare file1.json file2.json -o report.txt"
echo "  jcompare file1.json file2.json --format json -o report.json"
echo "  jfetch -c curl_command.txt -o response.json"
echo ""
echo "For help:"
echo "  jcompare --help"
echo "  jfetch --help"
