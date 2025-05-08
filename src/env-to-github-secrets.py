import click
import sys
from pathlib import Path
from dotenv import dotenv_values

cli = click.Group()

@cli.command()
@click.option(
    "--env-file", "-e", default=".env", help="Path to the .env file (default: .env)"
)
@click.option(
    "--colab-file",
    "-c",
    default="colab_env.py",
    help="Output file for Colab (default: colab_env.py)",
)
@click.option(
    "--secure-dir",
    "-s",
    default="~/.secure_colab",
    help="Directory to securely store the Colab file (default: ~/.secure_colab)",
)
@click.option(
    "--url",
    "-u",
    default=None,
    help="Optional Google Drive URL for Colab (e.g., https://colab.research.google.com/drive/...)",
)
def secure_upload_to_colab(env_file, colab_file, secure_dir, url):
    """Securely upload .env variables to Google Colab as a Python file"""
    # Check if .env file exists
    env_path = Path(env_file)
    if not env_path.exists():
        click.echo(f"Error: {env_file} not found")
        sys.exit(1)

    # Read .env file
    env_vars = dotenv_values(env_file)
    if not env_vars:
        click.echo(f"No variables found in {env_file}")
        sys.exit(1)

    click.echo(f"Found {len(env_vars)} variables in {env_file}")

    # Ensure secure directory exists
    secure_dir_path = Path(secure_dir).expanduser()
    secure_dir_path.mkdir(parents=True, exist_ok=True)

    # Write the Colab file to the secure directory
    secure_colab_file = secure_dir_path / colab_file
    try:
        with open(secure_colab_file, "w") as f:
            f.write(
                "# Auto-generated file for setting environment variables in Google Colab\n"
            )
            f.write("import os\n\n")
            for name, value in env_vars.items():
                sanitized_name = name.upper().replace("-", "_")
                f.write(f"os.environ['{sanitized_name}'] = '{value}'\n")
        click.echo(f"Environment variables securely written to {secure_colab_file}")
        if url:
            click.echo(f"Google Drive URL: {url}")
    except Exception as e:
        click.echo(f"Error writing to {secure_colab_file}: {e}")
        sys.exit(1)

    # Notify user to add secure directory to .gitignore
    gitignore_path = Path(".gitignore")
    try:
        with gitignore_path.open("a+") as gitignore:
            gitignore.seek(0)
            gitignore_content = gitignore.read()
            if str(secure_dir_path) not in gitignore_content:
                gitignore.write(f"\n# Secure Colab files\n{secure_dir_path}\n")
        click.echo(
            f"Added {secure_dir_path} to .gitignore to prevent accidental check-in"
        )
    except Exception as e:
        click.echo(f"Error updating .gitignore: {e}")
        sys.exit(1)

    # Remove the Colab file after successful execution
    try:
        secure_colab_file.unlink()
        click.echo(f"Temporary Colab file {secure_colab_file} removed after execution")
    except Exception as e:
        click.echo(f"Error removing temporary file {secure_colab_file}: {e}")
        sys.exit(1)


# Register the secure_upload_to_colab command
cli.add_command(secure_upload_to_colab)

if __name__ == "__main__":
    cli()
