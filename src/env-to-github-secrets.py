#!/usr/bin/env python3
"""
env-to-github-secrets.py - A CLI tool to convert .env files to GitHub Secrets

This tool reads a .env file and creates GitHub Secrets for each environment variable,
helping improve security by moving sensitive data from local unencrypted files
to GitHub's secure secrets storage.
"""

import os
import sys
import requests
import base64
import json
from pathlib import Path
from nacl import encoding, public
import click
import keyring
import getpass
from dotenv import dotenv_values


SERVICE_NAME = "env-to-github-secrets"
ACCOUNT_NAME = "github-pat"


def encrypt_secret(public_key, secret_value):
    """Encrypt a secret using GitHub's public key"""
    public_key_bytes = public.PublicKey(
        public_key.encode("utf-8"), encoding.Base64Encoder()
    )
    sealed_box = public.SealedBox(public_key_bytes)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def get_repo_public_key(owner, repo, token):
    """Get the public key for a repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        click.echo(f"Error fetching public key: {response.status_code} {response.text}")
        sys.exit(1)

    return response.json()


def create_or_update_secret(owner, repo, secret_name, encrypted_value, key_id, token):
    """Create or update a secret in the repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    data = {"encrypted_value": encrypted_value, "key_id": key_id}

    response = requests.put(url, headers=headers, data=json.dumps(data))

    if response.status_code not in [201, 204]:
        click.echo(
            f"Error creating/updating secret {secret_name}: {response.status_code} {response.text}"
        )
        return False
    return True


def store_github_token(token):
    """Store GitHub token in the system keyring"""
    keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, token)
    click.echo("GitHub token stored securely in system keyring")


def get_github_token():
    """Retrieve GitHub token from the system keyring"""
    token = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
    return token


@click.group()
def cli():
    """
    Tool to convert .env files to GitHub Secrets.
    """
    pass


@cli.command()
def setup():
    """Configure GitHub Personal Access Token (PAT)"""
    click.echo("Setting up GitHub Personal Access Token")
    click.echo(
        "Please create a PAT with 'repo' scope at: https://github.com/settings/tokens"
    )

    token = getpass.getpass("Enter your GitHub Personal Access Token: ")
    if not token.strip():
        click.echo("Token cannot be empty. Aborting.")
        sys.exit(1)

    store_github_token(token)
    click.echo("Setup complete!")


@cli.command()
@click.option(
    "--env-file", "-e", default=".env", help="Path to the .env file (default: .env)"
)
@click.option(
    "--github-repo", "-r", required=True, help="GitHub repository in format owner/repo"
)
@click.option(
    "--force", "-f", is_flag=True, help="Override existing secrets without confirmation"
)
def upload(env_file, github_repo, force):
    """Upload .env variables as GitHub Secrets"""
    # Check if .env file exists
    env_path = Path(env_file)
    if not env_path.exists():
        click.echo(f"Error: {env_file} not found")
        sys.exit(1)

    # Get GitHub token
    token = get_github_token()
    if not token:
        click.echo("GitHub token not found. Please run 'setup' command first.")
        sys.exit(1)

    # Parse owner and repo
    try:
        owner, repo = github_repo.split("/")
    except ValueError:
        click.echo("Error: GitHub repository must be in format 'owner/repo'")
        sys.exit(1)

    # Get repository public key
    try:
        key_data = get_repo_public_key(owner, repo, token)
        public_key = key_data["key"]
        key_id = key_data["key_id"]
    except Exception as e:
        click.echo(f"Error: Failed to get repository public key: {e}")
        sys.exit(1)

    # Read .env file
    env_vars = dotenv_values(env_file)
    if not env_vars:
        click.echo(f"No variables found in {env_file}")
        sys.exit(1)

    click.echo(f"Found {len(env_vars)} variables in {env_file}")

    # Upload each variable as a secret
    success_count = 0
    for name, value in env_vars.items():
        # GitHub Secrets must be named with uppercase letters, numbers, and underscores only
        github_secret_name = name.upper().replace("-", "_")

        if name != github_secret_name:
            click.echo(
                f"Note: Renamed '{name}' to '{github_secret_name}' to comply with GitHub naming rules"
            )

        # Encrypt the secret value
        encrypted_value = encrypt_secret(public_key, value)

        # Create or update the secret
        click.echo(f"Creating/updating secret: {github_secret_name}...", nl=False)

        if create_or_update_secret(
            owner, repo, github_secret_name, encrypted_value, key_id, token
        ):
            click.echo(" Done!")
            success_count += 1
        else:
            click.echo(" Failed!")

    click.echo(
        f"\nProcessed {len(env_vars)} variables: {success_count} successful, {len(env_vars) - success_count} failed"
    )


@cli.command()
@click.option(
    "--github-repo", "-r", required=True, help="GitHub repository in format owner/repo"
)
def list_secrets(github_repo):
    """List existing GitHub Secrets in the repository"""
    # Get GitHub token
    token = get_github_token()
    if not token:
        click.echo("GitHub token not found. Please run 'setup' command first.")
        sys.exit(1)

    # Parse owner and repo
    try:
        owner, repo = github_repo.split("/")
    except ValueError:
        click.echo("Error: GitHub repository must be in format 'owner/repo'")
        sys.exit(1)

    # List secrets
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        click.echo(f"Error fetching secrets: {response.status_code} {response.text}")
        sys.exit(1)

    secrets = response.json()["secrets"]

    if not secrets:
        click.echo(f"No secrets found in {github_repo}")
    else:
        click.echo(f"Secrets in {github_repo}:")
        for secret in secrets:
            # Format the creation and update dates
            created_at = secret["created_at"].split("T")[0]
            updated_at = secret["updated_at"].split("T")[0]
            click.echo(
                f"• {secret['name']} (Created: {created_at}, Updated: {updated_at})"
            )


if __name__ == "__main__":
    cli()
