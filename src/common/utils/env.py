def replace_env_var(source_file_path, target_file_path, env_var_name, env_var_value):
    with open(source_file_path, 'r') as file:
        env_content = file.readlines()

    with open(target_file_path, 'w') as file:
        new_git_branches_line = f'{env_var_name}={env_var_value}\n'
        for i, line in enumerate(env_content):
            if line.startswith('GIT_BRANCHES='):
                env_content[i] = new_git_branches_line
            else:
                env_content[i] = line

        file.writelines(env_content)
