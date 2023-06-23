import yaml
import re
import os


def store_config(config_files, filename, config):
    if filename not in config_files:
        config_files[filename] = [config]
    else:
        config_files[filename].append(config)


def write_config_files(config_files, path, separate=False):
    complete = {}

    try:
        for filename in config_files:
            mode = 'w'
            if filename in complete:
                mode = 'a'
            else:
                complete[filename] = 0

            full_path = os.path.join(path, filename)

            with open(full_path, mode) as file:
                for config in config_files[filename]:
                    if separate:
                        yaml.dump(config, file)
                    else:
                        yaml.dump([config], file)
                    complete[filename] += 1
                print(f"{full_path} generated successfully with {complete[filename]} entries.")

    except Exception as e:
        print(f"Error writing config files: {str(e)}")
        exit(1)


def create_filename(prefix, identifier, suffix):
    # Remove illegal characters
    filename = re.sub(r'[<>:"/\|?* \t]', '_', identifier)

    # Create a unique filename to avoid duplicates
    count = 1
    unique_identifier = filename.lower()
    while os.path.exists(unique_identifier):
        if count == 1:
            unique_identifier = f"{filename}"
        else:
            unique_identifier = f"{filename}_{count}"
        count += 1

    # Combine prefix, filename, and suffix
    final_filename = prefix + unique_identifier + suffix

    return final_filename

