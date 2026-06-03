#!/usr/bin/env bash
# Nice AI Agent — installer for macOS and Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/amrilsyaifa/Nice-AI-Agent/main/scripts/install.sh | bash

set -euo pipefail

REPO="amrilsyaifa/Nice-AI-Agent"
INSTALL_DIR="${NICE_INSTALL_DIR:-/usr/local/bin}"
BIN_NAME="nice"

# ── Detect platform ───────────────────────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Darwin)
    case "$ARCH" in
      arm64)  ASSET="nice-macos-arm64" ;;
      x86_64) ASSET="nice-macos-x86_64" ;;
      *)      echo "Unsupported macOS architecture: $ARCH" && exit 1 ;;
    esac
    ;;
  Linux)
    case "$ARCH" in
      x86_64) ASSET="nice-linux-x86_64" ;;
      *)      echo "Unsupported Linux architecture: $ARCH" && exit 1 ;;
    esac
    ;;
  *)
    echo "Unsupported OS: $OS"
    echo "For Windows, run: iwr https://raw.githubusercontent.com/$REPO/main/scripts/install.ps1 | iex"
    exit 1
    ;;
esac

# ── Get latest version ────────────────────────────────────────────────────
echo "Fetching latest release..."
VERSION="$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
  | grep '"tag_name"' | head -1 | cut -d'"' -f4)"

if [ -z "$VERSION" ]; then
  echo "Could not determine latest version. Check your internet connection."
  exit 1
fi

echo "Installing nice $VERSION ($ASSET)..."

# ── Download ──────────────────────────────────────────────────────────────
TMP="$(mktemp)"
curl -fsSL "https://github.com/$REPO/releases/download/$VERSION/$ASSET" -o "$TMP"
chmod +x "$TMP"

# ── Install ───────────────────────────────────────────────────────────────
if [ -w "$INSTALL_DIR" ]; then
  mv "$TMP" "$INSTALL_DIR/$BIN_NAME"
else
  echo "Installing to $INSTALL_DIR (requires sudo)..."
  sudo mv "$TMP" "$INSTALL_DIR/$BIN_NAME"
fi

# ── Verify ────────────────────────────────────────────────────────────────
echo ""
echo "Installed: $("$INSTALL_DIR/$BIN_NAME" version)"
echo ""
echo "Get started:"
echo "  nice config set api_key YOUR_API_KEY"
echo "  nice ask 'What is 2 + 2?'"
