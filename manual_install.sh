#!/bin/bash
# Manual installation script for Devin CLI

echo "🚀 Installing Devin CLI manually..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Install dependencies using the system Python
echo "📦 Installing dependencies..."
/opt/homebrew/opt/python@3.13/bin/python3.13 -m pip install click requests --user --break-system-packages 2>/dev/null || \
/opt/homebrew/opt/python@3.13/bin/python3.13 -m pip install click requests --user

# Create ~/.local/bin if it doesn't exist
LOCAL_BIN="$HOME/.local/bin"
if [ ! -d "$LOCAL_BIN" ]; then
    mkdir -p "$LOCAL_BIN"
    echo "📁 Created $LOCAL_BIN directory"
fi

# Get the absolute path to the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the devin-cli wrapper script
cat > "$LOCAL_BIN/devin-cli" << EOF
#!/bin/bash
# Devin CLI wrapper script
export PYTHONPATH="$SCRIPT_DIR:\$PYTHONPATH"
exec /opt/homebrew/opt/python@3.13/bin/python3.13 "$SCRIPT_DIR/devin_cli.py" "\$@"
EOF

# Make it executable
chmod +x "$LOCAL_BIN/devin-cli"
chmod +x "$SCRIPT_DIR/devin_cli.py"

echo "✅ Installation complete!"
echo ""
echo "📍 devin-cli installed to: $LOCAL_BIN/devin-cli"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" == *":$LOCAL_BIN:"* ]]; then
    echo "✅ ~/.local/bin is already in your PATH"
    echo "You can now run: devin-cli --help"
else
    echo "⚠️  ~/.local/bin is not in your PATH"
    echo "Add it to your shell profile:"
    echo ""
    echo "For zsh (default on macOS):"
    echo "  echo 'export PATH=\"\$PATH:$LOCAL_BIN\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo ""
    echo "For bash:"
    echo "  echo 'export PATH=\"\$PATH:$LOCAL_BIN\"' >> ~/.bash_profile"
    echo "  source ~/.bash_profile"
    echo ""
    echo "Or run directly: $LOCAL_BIN/devin-cli --help"
fi

echo ""
echo "🔑 Don't forget to set your API key:"
echo "  export DEVIN_API_KEY=your_token_here"
echo ""
echo "🧪 Test the installation:"
echo "  devin-cli --help"
