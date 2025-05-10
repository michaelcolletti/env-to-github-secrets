# ✨ env-to-github-secrets

[![Python Build Test and Deploy](https://github.com/michaelcolletti/env-to-github-secrets/actions/workflows/python-app-cicd.yml/badge.svg)](https://github.com/michaelcolletti/env-to-github-secrets/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)

A ⚡ powerful yet simple CLI tool to **convert `.env` files into GitHub Secrets**, ensuring your sensitive environment variables are securely managed inside GitHub repositories. No more unencrypted `.env` files lying around! 🚀

---

## 🎯 Features

- 🔒 **Securely** upload `.env` variables as GitHub Secrets.
- 🔑 Automatically store your **GitHub Personal Access Token (PAT)** in your system's keyring.
- 📋 **List existing GitHub Secrets** in a repository.
- 🛠️ Automatically format environment variable names to comply with GitHub's secret naming conventions.
- 💾 Uses GitHub's **recommended encryption** methods for secrets.

---

## 🚀 Quick Start

### 🛠️ Installation

#### Option 1: **Recommended - Using Makefile**

1. Clone this repository:
   ```bash
   git clone https://github.com/michaelcolletti/env-to-github-secrets.git
   cd env-to-github-secrets

    Build and install the project:
    bash

make install

🎉 Done! Everything is ready to go.

(Optional) Clean up build artifacts:
bash

    make clean

Option 2: Manual Installation
<details> <summary>Click to view manual installation steps</summary>

    Clone this repository:
    bash

git clone https://github.com/michaelcolletti/env-to-github-secrets.git
cd env-to-github-secrets

Install the required dependencies:
bash

pip install -r requirements.txt

Make the script executable:
bash

    chmod +x env-to-github-secrets.py

</details>
🖥️ Usage
1️⃣ Initial Setup

Before using this tool, you need to securely store your GitHub Personal Access Token (PAT):
bash

./env-to-github-secrets.py setup

You'll be prompted to enter your GitHub PAT. It will be securely stored in your system's keyring.

    Note: You can generate a PAT with repo scope at GitHub Developer Settings.

2️⃣ Upload .env Variables as Secrets

To upload all variables from a .env file to GitHub Secrets:
bash

./env-to-github-secrets.py upload --github-repo <owner/repo>

By default, it looks for a .env file in the current directory. To specify a different file:
bash

./env-to-github-secrets.py upload --env-file <path-to-env-file> --github-repo <owner/repo>

3️⃣ List Existing GitHub Secrets

To view all secrets in a repository:
bash

./env-to-github-secrets.py list-secrets --github-repo <owner/repo>

📚 Documentation
📝 Important Notes

    Secret Naming Rules:
        Secret names can only include uppercase letters, numbers, and underscores (_).
        Hyphens (-) are automatically converted to underscores (_) and all names are capitalized.

    Permissions Required:
        Read access to your local .env file.
        Write access to GitHub Secrets for the specified repository (via your PAT).

    Security First:
        Your GitHub PAT is stored securely in your system's keyring (not in plaintext).
        The tool uses encryption recommended by GitHub for creating secrets.
        No sensitive data is logged to the console.

🔧 Requirements

    Python 3.6+
    Required Python packages (see requirements.txt):
        click
        requests
        python-dotenv
        pynacl
        keyring

🔒 Security Considerations

    Your GitHub PAT is securely stored in your system's keyring, not in plaintext.
    All secrets uploaded to GitHub are encrypted using GitHub's secure API methods.
    The tool avoids logging any sensitive information to the console.


⭐ Acknowledgments

    Inspired by the need for better security practices in managing .env files.
    
🌟 Enjoy a simpler, more secure way to manage GitHub Secrets! Stay tuner for a Colab version!
