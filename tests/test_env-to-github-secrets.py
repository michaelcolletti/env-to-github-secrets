import sys
from pathlib import Path
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from src.env_to_github_secrets import cli

# Add project root to sys.path to allow importing from src
# Assumes test file is in /tests/ and src is in /src/ at project root
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))


@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def temp_env_file_fixture(tmp_path):
    env_content = "TEST_VAR1=value1\nMY-VAR-2=another_value\n#COMMENT_VAR=commented\n"
    env_file = tmp_path / ".env.test"
    env_file.write_text(env_content)
    return env_file

@pytest.fixture
def empty_env_file_fixture(tmp_path):
    env_file = tmp_path / ".env.empty.test"
    env_file.write_text("")
    return env_file

@pytest.fixture
def temp_secure_dir_fixture(tmp_path):
    # The script creates the directory, so this fixture just provides the path
    return tmp_path / "secure_colab_test_dir"

def test_secure_upload_to_colab_success(runner, temp_env_file_fixture, temp_secure_dir_fixture, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path) # To handle Path(".gitignore") correctly
    
    # Create a dummy .gitignore file in the new CWD (tmp_path)
    actual_gitignore_file = tmp_path / ".gitignore"
    actual_gitignore_file.touch()

    colab_file_name = "colab_env_test.py"

    result = runner.invoke(
        cli,
        [
            "secure-upload-to-colab",
            "--env-file", str(temp_env_file_fixture),
            "--colab-file", colab_file_name,
            "--secure-dir", str(temp_secure_dir_fixture),
        ],
    )

    assert result.exit_code == 0, f"CLI Error: {result.output} {result.exception}"
    assert f"Found 2 variables in {temp_env_file_fixture}" in result.output
    
    secure_colab_file_path = temp_secure_dir_fixture / colab_file_name
    assert f"Environment variables securely written to {secure_colab_file_path}" in result.output
    
    assert actual_gitignore_file.exists()
    gitignore_content = actual_gitignore_file.read_text()
    # The script uses secure_dir_path directly, which is absolute if tmp_path is absolute
    assert str(temp_secure_dir_fixture) in gitignore_content 
    assert f"Added {str(temp_secure_dir_fixture)} to .gitignore" in result.output

    assert f"Temporary Colab file {secure_colab_file_path} removed after execution" in result.output
    assert not secure_colab_file_path.exists() # Check it was removed

def test_secure_upload_to_colab_content_check(runner, temp_env_file_fixture, temp_secure_dir_fixture, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    actual_gitignore_file = tmp_path / ".gitignore"
    actual_gitignore_file.touch()
    colab_file_name = "colab_env_content_test.py"
    secure_colab_file_path = temp_secure_dir_fixture / colab_file_name

    with patch.object(Path, "unlink") as mock_unlink:
        result = runner.invoke(
            cli,
            [
                "secure-upload-to-colab",
                "--env-file", str(temp_env_file_fixture),
                "--colab-file", colab_file_name,
                "--secure-dir", str(temp_secure_dir_fixture),
            ],
        )
    
    assert result.exit_code == 0, f"CLI Error: {result.output} {result.exception}"
    assert secure_colab_file_path.exists() # Should exist because unlink is mocked
    
    content = secure_colab_file_path.read_text()
    assert "# Auto-generated file for setting environment variables in Google Colab" in content
    assert "import os" in content
    assert "os.environ['TEST_VAR1'] = 'value1'" in content
    assert "os.environ['MY_VAR_2'] = 'another_value'" in content # Check sanitization
    assert "COMMENT_VAR" not in content # Comments should be ignored by dotenv_values

    mock_unlink.assert_called_once() 

    # Clean up the file manually since unlink was mocked
    if secure_colab_file_path.exists():
        secure_colab_file_path.unlink()

def test_env_file_not_found(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    non_existent_env_file = tmp_path / "does_not_exist.env"
    # Provide a secure_dir to avoid default home dir usage, even if command fails early
    secure_dir = tmp_path / "secure_test_not_found"

    result = runner.invoke(
        cli,
        [
            "secure-upload-to-colab",
            "--env-file", str(non_existent_env_file),
            "--secure-dir", str(secure_dir) 
        ],
    )
    assert result.exit_code == 1
    assert f"Error: {non_existent_env_file} not found" in result.output

def test_empty_env_file(runner, empty_env_file_fixture, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    secure_dir = tmp_path / "secure_test_empty_env"
    result = runner.invoke(
        cli,
        [
            "secure-upload-to-colab",
            "--env-file", str(empty_env_file_fixture),
            "--secure-dir", str(secure_dir)
        ],
    )
    assert result.exit_code == 1
    assert f"No variables found in {empty_env_file_fixture}" in result.output

def test_custom_paths_and_url(runner, temp_env_file_fixture, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    custom_colab_name = "my_special_colab.py"
    custom_secure_dir = tmp_path / "my_secure_files_custom"
    custom_url = "http://example.com/colab_link"
    
    actual_gitignore_file = tmp_path / ".gitignore"
    actual_gitignore_file.touch()

    with patch.object(Path, "unlink"): # Mock unlink to check file existence
        result = runner.invoke(
            cli,
            [
                "secure-upload-to-colab",
                "--env-file", str(temp_env_file_fixture),
                "--colab-file", custom_colab_name,
                "--secure-dir", str(custom_secure_dir),
                "--url", custom_url,
            ],
        )

    assert result.exit_code == 0, f"CLI Error: {result.output} {result.exception}"
    assert f"Found 2 variables in {temp_env_file_fixture}" in result.output
    
    secure_colab_file_path = custom_secure_dir / custom_colab_name
    assert f"Environment variables securely written to {secure_colab_file_path}" in result.output
    assert secure_colab_file_path.exists() 

    assert f"Google Drive URL: {custom_url}" in result.output
    
    gitignore_content = actual_gitignore_file.read_text()
    assert str(custom_secure_dir) in gitignore_content
    assert f"Added {str(custom_secure_dir)} to .gitignore" in result.output
    
    if secure_colab_file_path.exists():
        secure_colab_file_path.unlink()

def test_gitignore_already_contains_path(runner, temp_env_file_fixture, temp_secure_dir_fixture, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    actual_gitignore_file = tmp_path / ".gitignore"
    
    initial_gitignore_content = f"\n# Secure Colab files\n{str(temp_secure_dir_fixture)}\n"
    actual_gitignore_file.write_text(initial_gitignore_content)

    with patch.object(Path, "unlink"): # Mock unlink
        result = runner.invoke(
            cli,
            [
                "secure-upload-to-colab",
                "--env-file", str(temp_env_file_fixture),
                "--secure-dir", str(temp_secure_dir_fixture),
            ],
        )

    assert result.exit_code == 0, f"CLI Error: {result.output} {result.exception}"
    # The "Added ... to .gitignore" message is printed even if the line already exists,
    # because the check is for not writing, but the message is unconditional after the attempt.
    assert f"Added {str(temp_secure_dir_fixture)} to .gitignore" in result.output
    
    final_gitignore_content = actual_gitignore_file.read_text()
    # Ensure the path is not added a second time
    assert final_gitignore_content.count(str(temp_secure_dir_fixture)) == 1
    
    secure_colab_file_path = temp_secure_dir_fixture / "colab_env.py" # Default name
    if secure_colab_file_path.exists():
         secure_colab_file_path.unlink()

def test_colab_file_write_error(runner, temp_env_file_fixture, temp_secure_dir_fixture, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    colab_file_name = "colab_env_write_fail.py"
    secure_colab_file_path = temp_secure_dir_fixture / colab_file_name
    
    # Store original open to use for non-mocked calls
    original_builtin_open = open

    def faulty_open_side_effect(file_path_arg, mode='r', *args, **kwargs):
        # If this is the call to write the colab file, raise an error
        if str(file_path_arg) == str(secure_colab_file_path) and 'w' in mode:
            raise IOError("Simulated permission denied")
        # Otherwise, delegate to the original open (for .env reading, .gitignore, etc.)
        return original_builtin_open(file_path_arg, mode, *args, **kwargs)

    with patch('builtins.open', side_effect=faulty_open_side_effect):
        result = runner.invoke(
            cli,
            [
                "secure-upload-to-colab",
                "--env-file", str(temp_env_file_fixture),
                "--colab-file", colab_file_name,
                "--secure-dir", str(temp_secure_dir_fixture),
            ],
        )

    assert result.exit_code == 1
    assert f"Error writing to {secure_colab_file_path}" in result.output
    assert "Simulated permission denied" in result.output
    assert not secure_colab_file_path.exists()

def test_default_filenames_and_paths(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path) # CWD is now tmp_path
    
    # Create default .env file in CWD (tmp_path)
    default_env_content = "DEFAULT_VAR=default_value_in_cwd_env"
    default_env_file_in_cwd = tmp_path / ".env" 
    default_env_file_in_cwd.write_text(default_env_content)

    # Must provide secure_dir for safe testing, overriding ~/.secure_colab
    test_secure_dir = tmp_path / "test_secure_colab_for_defaults"
    
    actual_gitignore_file = tmp_path / ".gitignore"
    actual_gitignore_file.touch()

    default_colab_filename = "colab_env.py" # Default name for colab file
    expected_secure_colab_path = test_secure_dir / default_colab_filename

    with patch.object(Path, "unlink") as mock_unlink:
        result = runner.invoke(
            cli,
            [
                "secure-upload-to-colab",
                # No --env-file, should use ./.env (which is tmp_path/.env)
                # No --colab-file, should use colab_env.py
                "--secure-dir", str(test_secure_dir), # Override default ~/.secure_colab
            ],
        )

    assert result.exit_code == 0, f"CLI Error: {result.output} {result.exception}"
    # The script resolves env_file path, so it will be absolute
    assert f"Found 1 variables in {default_env_file_in_cwd.resolve()}" in result.output
    
    assert f"Environment variables securely written to {expected_secure_colab_path}" in result.output
    assert expected_secure_colab_path.exists() 
    
    content = expected_secure_colab_path.read_text()
    assert "os.environ['DEFAULT_VAR'] = 'default_value_in_cwd_env'" in content

    mock_unlink.assert_called_once_with() # Check unlink was called on the correct path (instance)
    
    if expected_secure_colab_path.exists():
        expected_secure_colab_path.unlink()
