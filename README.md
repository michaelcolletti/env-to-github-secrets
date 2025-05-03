# env-to-github-secrets

A simple CLI tool that converts local `.env` files to GitHub Secrets, improving your application's security by moving sensitive environment variables from unencrypted local files to GitHub's secure secrets storage.

## Features

- Reads `.env` files and creates GitHub Secrets for each variable
- Securely stores GitHub Personal Access Token in your system's keyring
- Supports listing existing GitHub Secrets in a repository
- Automatically formats environment variable names to comply with GitHub Secret naming rules

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/michaelcolletti/env-to-github-secrets.git
   cd env-to-github-secrets
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make the script executable:
   ```
   chmod +x env-to-github-secrets.py
   ```

## Usage

### Initial Setup

Before using the tool, you need to store your GitHub Personal Access Token (PAT):

```
./env-to-github-secrets.py setup
```

You'll be prompted to enter your GitHub PAT, which will be securely stored in your system's keyring.

> **Note**: Create a PAT with the `repo` scope at https://github.com/settings/tokens

### Upload .env Variables as GitHub Secrets

To upload all variables from a `.env` file to GitHub Secrets:

```
./env-to-github-secrets.py upload --github-repo michaelcolletti/repository
```

By default, the tool looks for a `.env` file in the current directory. You can specify a different file:

```
./env-to-github-secrets.py upload --env-file .env.production --github-repo michaelcolletti/repository
```

### List Existing GitHub Secrets

To view existing GitHub Secrets in a repository:

```
./env-to-github-secrets.py list-secrets --github-repo michaelcolletti/repository
```

## Important Notes

1. GitHub Secret names can only include uppercase letters, numbers, and underscores. The tool automatically converts any hyphens to underscores and makes all secret names uppercase.

2. Your GitHub PAT is stored securely in your system's keyring, not in any file.

3. The tool requires the following permissions:
   - Read access to your local `.env` file
   - Write access to GitHub Secrets for the specified repository (via your PAT)

## Requirements

- Python 3.6+
- Required packages (see requirements.txt):
  - click
  - requests
  - python-dotenv
  - pynacl
  - keyring

## Security Considerations

- Your GitHub PAT is stored in your system's secure keyring, not in plaintext
- The tool uses GitHub's recommended encryption method for creating secrets
- No sensitive data is logged to the console

## License

[MIT License](LICENSE)