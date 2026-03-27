#!/bin/bash

# ============================================
# Helix-Zero Setup Script (Mac/Linux)
# ============================================

echo "🧬 Helix-Zero Setup Script"
echo "=========================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo ""
    echo "Please install Node.js first:"
    echo "  - Mac: brew install node"
    echo "  - Ubuntu: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "  - Or download from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js installed: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed!"
    exit 1
fi

NPM_VERSION=$(npm -v)
echo "✅ npm installed: $NPM_VERSION"

# Check Git
if ! command -v git &> /dev/null; then
    echo "⚠️  Git is not installed (optional for local development)"
else
    GIT_VERSION=$(git --version)
    echo "✅ $GIT_VERSION"
fi

echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Starting development server..."
    echo ""
    echo "======================================"
    echo "  Open http://localhost:5173 in your browser"
    echo "======================================"
    echo ""
    npm run dev
else
    echo ""
    echo "❌ Failed to install dependencies"
    echo "Try running: npm install --legacy-peer-deps"
    exit 1
fi
