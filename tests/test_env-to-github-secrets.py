import env_to_github_secrets as env_to_github_secrets
# create test cases for the function src/env_to_github_secrets
def test_get_env_vars():
    # test with a .env file
    env_vars = env_to_github_secrets.get_env_vars('.env')
    assert isinstance(env_vars, dict)
    assert len(env_vars) > 0
    # test with a non-existent file
    env_vars = env_to_github_secrets.get_env_vars('non_existent_file.env')
    assert env_vars is None
    # test with an empty file
    with open('empty_file.env', 'w') as f:
        pass
    env_vars = env_to_github_secrets.get_env_vars('empty_file.env')
    assert env_vars == {}
    # test with a file with invalid format
    with open('invalid_file.env', 'w') as f:
        f.write('INVALID_FORMAT')
    env_vars = env_to_github_secrets.get_env_vars('invalid_file.env')
    assert env_vars == {}
    
