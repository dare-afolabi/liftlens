#!/usr/bin/env bash
set -euo pipefail

echo "============================"
echo "🚀 Starting Local Workflow Mimic"
echo "============================"

# -------------------------
# 1️⃣ Activate Poetry environment
# -------------------------
echo "🔹 Activating Poetry environment..."
VENV_PATH=$(poetry env info --path)
if [ -z "$VENV_PATH" ]; then
    echo "❌ No Poetry virtual environment found. Please run 'poetry install --with dev' first."
    exit 1
fi
export PATH="$VENV_PATH/bin:$PATH"
echo "✅ Activated virtual environment at $VENV_PATH"
python --version

# -------------------------
# 2️⃣ Lint (ruff)
# -------------------------
echo "============================"
echo "🧹 Running Lint (ruff)..."
ruff --version
ruff check .

# -------------------------
# 3️⃣ Type check (mypy)
# -------------------------
echo "============================"
echo "📝 Running Type Check (mypy)..."
mypy --version
mypy src --ignore-missing-imports --pretty

# -------------------------
# 4️⃣ Run tests (pytest)
# -------------------------
echo "============================"
echo "🧪 Running Tests (pytest)..."
pytest --version
pytest -q --cov=src/liftlens --cov-report=xml --cov-report=term-missing -v

# -------------------------
# 5️⃣ Build distributions
# -------------------------
echo "============================"
echo "📦 Building Distributions..."
python -m build --sdist --wheel

# -------------------------
# 6️⃣ Validate distributions (twine)
# -------------------------
echo "============================"
echo "🔍 Validating Distributions..."
python -m twine --version
python -m twine check dist/*

# -------------------------
# 7️⃣ Optional: Release simulation
# -------------------------
echo "============================"
echo "🏷️ Simulating Release (local only)..."
echo "Skipping actual PyPI publish to avoid accidental uploads."
echo "You can run 'poetry publish --repository testpypi' manually if desired."

# -------------------------
# 8️⃣ Done
# -------------------------
echo "============================"
echo "🎉 All workflows mimicked successfully!"
echo "Lint, type-check, tests, coverage, build, and distribution validation complete."
echo "============================"