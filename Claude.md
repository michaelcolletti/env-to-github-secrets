# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Setup
- `make install` - Install dependencies (recommended method)
- `pip install -r requirements.txt` - Manual dependency installation

### Testing and Quality
- `make test` - Run pytest tests with coverage and flake8 linting
- `python -m pytest -vv tests/*.py` - Run tests only
- `make format` - Format code using black
- `make lint` - Run pylint on main.py

### Development Workflow
- `make all` - Complete workflow: install, format, lint, test, run
- `make clean` - Remove build artifacts and cache files
- `python src/main.py` or `python src/env-to-github-secrets.py` - Run the CLI tool

## Project Architecture

This is a CLI tool that converts `.env` files to GitHub Secrets using the GitHub API. The main application logic is duplicated in two files:

### Core Components
- **src/main.py** and **src/env-to-github-secrets.py** - Identical CLI implementations using Click framework
- **Core functions**:
  - `encrypt_secret()` - Encrypts values using GitHub's public key with PyNaCl
  - `get_repo_public_key()` - Fetches repository public key from GitHub API
  - `create_or_update_secret()` - Creates/updates secrets via GitHub API
  - `store_github_token()` / `get_github_token()` - Secure token storage using system keyring

### CLI Commands
- `setup` - Configure GitHub Personal Access Token (stored in system keyring)
- `upload` - Upload .env variables as GitHub Secrets
- `list-secrets` - List existing GitHub Secrets in a repository

### Security Features
- GitHub PAT stored securely in system keyring (not plaintext)
- Secrets encrypted using GitHub's recommended PyNaCl encryption
- Environment variable names auto-formatted to GitHub naming conventions (uppercase, underscores only)

### Testing
- Uses pytest with coverage reporting
- Test configuration in pytest.ini
- Tests are incomplete/placeholder in current state