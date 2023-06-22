#!/usr/bin/env python3
import argparse
import yaml
from lib.yaml_parser import load_yaml_data
from lib.version_manager import process_data


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prompath', default='./compose/prometheus/files_sd/', help='The path in which generated Prometheus configuration files will be stored (default: %(default)s)')
    parser.add_argument('-e', '--emepath', default='./compose/ethereum-metrics-exporter/', help='The path in which generated Ethereum Metrics Exporter configuration files will be stored (default: %(default)s)')
    parser.add_argument("yaml_filename", help='StakeLocal YAML configuration filename')
    args = parser.parse_args()

    # Check if YAML filename is provided
    if not args.yaml_filename:
        parser.error('No YAML filename provided.')
        parser.print_help()
        exit(1)

    # Extract command-line arguments
    yaml_filename = args.yaml_filename
    prompath = args.prompath
    emepath = args.emepath

    try:
        # Load YAML file
        data = load_yaml_data(yaml_filename)

        # Process data based on the version
        process_data(data, prompath, emepath)

        # Print a success message
        print("Configuration completed successfully.")

    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {str(e)}")
        exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()

