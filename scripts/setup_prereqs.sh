#!/bin/bash
# Skhand v0.1 — Prerequisites Setup Script
# Run this in your terminal: bash ~/skhand/scripts/setup_prereqs.sh
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  स्कन्ध — Skhand Prerequisites Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Homebrew ─────────────────────────────────
if command -v brew &>/dev/null; then
    echo "✓ Homebrew already installed: $(brew --version | head -1)"
else
    echo "→ Installing Homebrew (will ask for your password)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add to PATH for this session and permanently
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        echo "✓ Homebrew installed and added to PATH"
    elif [ -f /usr/local/bin/brew ]; then
        eval "$(/usr/local/bin/brew shellenv)"
        echo "✓ Homebrew installed (Intel path)"
    else
        echo "✗ Homebrew install location not found. Please check manually."
        exit 1
    fi
fi

# Ensure brew is on PATH for rest of script
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# ── Step 2: Python 3.12 ─────────────────────────────
if command -v python3.12 &>/dev/null; then
    echo "✓ Python 3.12 already installed: $(python3.12 --version)"
else
    echo "→ Installing Python 3.12..."
    brew install python@3.12
    echo "✓ Python 3.12 installed: $(python3.12 --version)"
fi

# ── Step 3: Docker Desktop ──────────────────────────
if command -v docker &>/dev/null; then
    echo "✓ Docker already installed: $(docker --version)"
else
    echo "→ Installing Docker Desktop..."
    brew install --cask docker
    echo "✓ Docker Desktop installed"
    echo "  ⚠ Please open Docker Desktop from Applications to start it"
    open -a Docker 2>/dev/null || echo "  (open it manually from Applications)"

    echo ""
    echo "  Waiting for Docker to start..."
    for i in {1..30}; do
        if docker info &>/dev/null 2>&1; then
            echo "  ✓ Docker is running"
            break
        fi
        sleep 2
        printf "."
    done
    echo ""
fi

# ── Step 4: Recreate venv with Python 3.12 ──────────
echo ""
echo "→ Setting up Python 3.12 venv for Skhand..."
cd ~/skhand

if [ -d .venv ]; then
    echo "  Removing old Python 3.9 venv..."
    rm -rf .venv
fi

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel -q
pip install -e ".[dev]" -q
echo "✓ Skhand installed with Python 3.12 venv"

# ── Step 5: Start Neo4j ─────────────────────────────
if docker info &>/dev/null 2>&1; then
    echo ""
    echo "→ Starting Neo4j container..."
    cd ~/skhand
    docker compose up -d
    echo "✓ Neo4j starting on localhost:7474 (user: neo4j, pass: skhand2026)"

    # Wait for Neo4j to be ready
    echo "  Waiting for Neo4j..."
    for i in {1..20}; do
        if curl -s http://localhost:7474 &>/dev/null; then
            echo "  ✓ Neo4j is ready"
            break
        fi
        sleep 2
        printf "."
    done
    echo ""

    # Seed the graph
    echo "→ Seeding knowledge graph..."
    .venv/bin/skhand graph build
else
    echo ""
    echo "⚠ Docker not running yet. Start Docker Desktop, then run:"
    echo "  cd ~/skhand && docker compose up -d && .venv/bin/skhand graph build"
fi

# ── Done ─────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Set your API key:  Edit ~/skhand/.env"
echo "  2. Activate venv:     cd ~/skhand && source .venv/bin/activate"
echo "  3. Check status:      skhand status"
echo "  4. Ask a question:    skhand ask \"What is Rajata Bhasma?\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
