# Install uv
unix based OS: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex`.

# Setup up
```bash
uv init --name Calculator
```

# Create virtual environment
```bash
uv venv --python 3.14
```

# Activate the virtual environment
unix
```bash
source .venv/bin/activate
```

Windows:
```PS
.venv\Scripts\activate
```

# Deactivate the virtual environment
```bash
deactivate
```

# Run a specific file
```bash
uv run <path to file>
```

# Run the app
```bash
uv run calculator
```

# Add packages for prod
```bash
uv add <package name>
```
# Add packages for development
```bash
uv add --dev pytest
```
# Install all the dependencies from pyprojec.toml
```bash
uv sync
```
# Install only prod dependencies from pyprojec.toml
```bash
uv sync --no-dev
```
# remove packages
prod packages:
```bash
uv remove <package name>
```
dev packages:
```bash
uv remove --dev <package name>
```

# Check types
```bash
uv run mypy src/
```

# Run linting
```bash
uv run pylint src/
```