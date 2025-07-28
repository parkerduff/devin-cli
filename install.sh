#!/bin/bash
# Installation script for Devin CLI

echo "Installing Devin CLI..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Try to install the package in development mode
echo "Installing devin-cli package..."

# Try different installation methods
if command -v pip3 &> /dev/null; then
    echo "Using pip3 to install..."
    pip3 install -e . --user
elif python3 -m pip --version &> /dev/null; then
    echo "Using python3 -m pip to install..."
    python3 -m pip install -e . --user
else
    echo "❌ pip not found. Installing dependencies manually..."
    if command -v pip3 &> /dev/null; then
        pip3 install click requests --user
    else
        echo "❌ Cannot install dependencies. Please install manually:"
        echo "  - click>=8.0.0"
        echo "  - requests>=2.25.0"
        exit 1
    fi
    
    # Create a symlink or copy to make it available globally
    echo "Creating executable..."
    chmod +x devin_cli.py
    
    # Try to add to PATH
    LOCAL_BIN="$HOME/.local/bin"
    if [ ! -d "$LOCAL_BIN" ]; then
        mkdir -p "$LOCAL_BIN"
    fi
    
    # Create a wrapper script
    cat > "$LOCAL_BIN/devin-cli" << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$(dirname "$DIR")/Repositories/apps/devin-cli/devin_cli.py" "$@"
EOF
    chmod +x "$LOCAL_BIN/devin-cli"
    
    echo "✅ Created devin-cli in $LOCAL_BIN"
    echo "Make sure $LOCAL_BIN is in your PATH:"
    echo "  export PATH=\$PATH:$LOCAL_BIN"
fi

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  devin-cli --help"
echo ""
echo "Don't forget to set your API key:"
echo "  export DEVIN_API_KEY=your_token_here"
echo ""
echo "If 'devin-cli' command is not found, add ~/.local/bin to your PATH:"
echo "  echo 'export PATH=\$PATH:~/.local/bin' >> ~/.zshrc"
echo "  source ~/.zshrc"
