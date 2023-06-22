import yaml


def load_yaml_data(filename):
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML file '{filename}' not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file '{filename}': {str(e)}")

