import re
from lib.file_writer import store_config, write_config_files, create_filename
from lib.constants import DEFAULT_GROUP, DEFAULT_HOST, DEFAULT_NETWORK, DEFAULT_CON_EXPLORER, DEFAULT_EXE_EXPLORER, DEFAULT_CURRENCIES, GITHUB_CLIENT_NAMES, CONSENSUS_CLIENTS, EXECUTION_CLIENTS, SERVICE_TYPE_VALIDATOR, SERVICE_TYPE_CONSENSUS, SERVICE_TYPE_EXECUTION, SERVICE_TYPE_JSON_EXPORTER, SERVICE_TYPE_GRAFANA, SERVICE_TYPE_PROMETHEUS, SERVICE_TYPE_NODE_EXPORTER, SERVICE_TYPE_BLACKBOX_EXPORTER, SERVICE_TYPE_ETH_METRICS

def process_data_v1_0(data, prompath=None, emepath=None):
    try:
        if prompath is not None:
            config_files = generate_target_configurations(data)
            write_config_files(config_files, prompath)

        if emepath is not None:
            config_files = generate_ethereum_metrics_exporter_configurations(data)
            write_config_files(config_files, emepath, True)

    except Exception as e:
        # Handle any specific exceptions here or log the error
        print(f"Error processing data: {str(e)}")


def generate_target_configurations(data):

    config_files = {}

    # Create group-specific targets
    for group in data['staking_groups']:

        for service in group['services']:

            service_type = service.get('service_type', None)
            if service_type == None:
                print('Missing service_type')
                continue

            # Run appropriate target generation based on the service_type
            service_type = service_type.lower()
            if service_type == SERVICE_TYPE_CONSENSUS:
                if 'software' in service and service['software'].lower() in CONSENSUS_CLIENTS:
                    generate_con_client_api_targets(group, service, config_files)
                    generate_con_client_metrics_targets(group, service, config_files)
            elif service_type == SERVICE_TYPE_VALIDATOR:
                if 'software' in service and service['software'].lower() in CONSENSUS_CLIENTS:
                    generate_val_client_metrics_targets(group, service, config_files)
            elif service_type == SERVICE_TYPE_EXECUTION:
                if 'software' in service and service['software'].lower() in EXECUTION_CLIENTS:
                    generate_exe_client_api_targets(group, service, config_files)
                    generate_exe_client_metrics_targets(group, service, config_files)

        if 'fee_addresses' in group:
            generate_fee_addresses_targets(group, group['fee_addresses'], config_files)

        if 'validators' in group:
            generate_validator_targets(group, group['validators'], config_files)

        service_ethereum_metrics_exporter = None
        if 'services' in group:
            service_ethereum_metrics_exporter = matching_record = next((service for service in group['services'] if service['service_type'] == SERVICE_TYPE_ETH_METRICS), None)

        # Reasonable defaults will be created for these if not present in the YAML file.
        generate_ethereum_metrics_exporter_targets(group, service_ethereum_metrics_exporter, config_files)

    service_prometheus = None
    service_json_exporter = None
    service_grafana = None
    service_node_exporters = None
    service_blackbox_exporter = None

    # Look for any shared_services defgined in the config file, to be
    # passed to our target generation, if found.
    # Also look for an create node_exporter targets if shared_services exists.
    if 'shared_services' in data:
        service_grafana = next((service for service in data['shared_services'] if service['service_type'] == SERVICE_TYPE_GRAFANA), None)
        service_json_exporter = next((service for service in data['shared_services'] if service['service_type'] == SERVICE_TYPE_JSON_EXPORTER), None)
        service_prometheus = next((service for service in data['shared_services'] if service['service_type'] == SERVICE_TYPE_PROMETHEUS), None)
        service_blackbox_exporter = next((service for service in data['shared_services'] if service['service_type'] == SERVICE_TYPE_BLACKBOX_EXPORTER), None)

        # node_exporter targets are created together so we can determine
        # if the local node_exporter service should be configured
        # as a target. Find all the node_exporter configs here.
        service_node_exporters = [service for service in data['shared_services'] if service.get('service_type') == SERVICE_TYPE_NODE_EXPORTER]

    # With or without shared_services, we create the following targets,
    # Any config info in shared_services is used to overried default values.
    generate_grafana_target(service_grafana, config_files)
    generate_prometheus_target(service_prometheus, config_files)
    generate_json_exporter_target(service_json_exporter, config_files)
    generate_blackbox_exporter_target(service_blackbox_exporter, config_files)

    generate_node_exporter_targets(service_node_exporters, config_files)

    currencies = DEFAULT_CURRENCIES + data.get('currencies', [])
    generate_currency_targets(currencies, config_files)

    generate_github_targets(config_files)

    return config_files


def generate_val_client_metrics_targets(group, service, config_files):

    software = service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Validator Client')

    config = {
        'labels': {
            'service': service.get('service_name', software_name + " Validator"),
            'host': service.get('host', DEFAULT_HOST),
            'network': group.get('network', DEFAULT_NETWORK),
            'group': group.get('group_name', DEFAULT_GROUP)
        },
        'targets': [service['metrics_address']]
    }

    filename = f'val_metrics_{software}.yml'
    store_config(config_files, filename, config)


def generate_exe_client_metrics_targets(group, service, config_files):

    software = service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Execution Client')

    config = {
        'labels': {
            'service': service.get('service_name', software_name),
            'host': service.get('host', DEFAULT_HOST),
            'network': group.get('network', DEFAULT_NETWORK),
            'explorer': group.get('execution explorer', DEFAULT_EXE_EXPLORER),
            'group': group.get('group_name', DEFAULT_GROUP)
        },
        'targets': [service['metrics_address']]
    }

    filename = f'exe_metrics_{software}.yml'
    store_config(config_files, filename, config)


def generate_exe_client_api_targets(group, service, config_files):

    software = service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Execution Client')

    config = {
        'labels': {
            'service': service.get('service_name', software_name),
            'host': service.get('host', DEFAULT_HOST),
            'explorer': group.get('execution explorer', DEFAULT_EXE_EXPLORER),
            'json_exporter': 'json-exporter:7979',
            'network': group.get('network', DEFAULT_NETWORK),
            'group': group.get('group_name', DEFAULT_GROUP),
            'client': software_name,
        },
        'targets': [service['api_address']]
    }

    filename = f'exe_api_{software}.yml'
    store_config(config_files, filename, config)


def generate_con_client_metrics_targets(group, service, config_files):

    software = service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Consensus Client')

    config = {
        'labels': {
            'host': service.get('host', DEFAULT_HOST),
            'network': group.get('network', DEFAULT_NETWORK),
            'explorer': group.get('consensus explorer', DEFAULT_CON_EXPLORER),
            'group': group.get('group_name', DEFAULT_GROUP),
            'service': service.get('service_name', software_name + " Beacon")
        },
        'targets': [service['metrics_address']]
    }

    filename = f'con_metrics_{software}.yml'
    store_config(config_files, filename, config)


def generate_con_client_api_targets(group, service, config_files):

    software = service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Consensus Client')

    config = {
        'labels': {
            'service': service.get('service_name', software_name + " Beacon"),
            'host': service.get('host', DEFAULT_HOST),
            'explorer': group.get('consensus explorer', DEFAULT_CON_EXPLORER),
            'network': group.get('network', DEFAULT_NETWORK),
            'group': group.get('group_name', DEFAULT_GROUP)
        },
        'targets': [service['api_address']]
    }

    filename = f'con_api_{software}.yml'
    store_config(config_files, filename, config)


def generate_node_exporter_targets(services, config_files):

    config = None
    local_used = False
    filename = 'node_exporter.yml'

    software_name = GITHUB_CLIENT_NAMES.get('node-exporter', 'Node Exporter')

    if services is not None:
        for service in services:
            
            # If metrics_api is present, then it is a custom configuration.
            # No special logic needed.
            if 'metrics_address' in service:
    
                config = {
                    'labels': {
                        'client': software_name,
                        'host': service.get('host', DEFAULT_HOST),
                        'service': service.get('service_name', 'Node Exporter')
                    },
                    'targets': [service['metrics_address']]
                }

                store_config(config_files, filename, config)

            # Without a metrics_api, we can use the local node_exporter,
            # but only the first one.
            else:
    
                if local_used:
                    # We don't have another local node_exporter to use.
                    print('node_exporter container already in use. Specify "metrics_api" for additional node_exporter instances.')
                else:
                    config = {
                        'labels': {
                            'client': software_name,
                            'host': service.get('host', DEFAULT_HOST),
                            'service': service.get('service_name', 'Node Exporter')
                        },
                        'targets': ['node-exporter:9100']
                    }

                    local_used = True
                    store_config(config_files, filename, config)

    # If we haven't created any node_exporter targets yet, then we
    # create one for the docker host system with a generic host name.
    if filename not in config_files:
        config = {
            'labels': {
                'client': software_name,
                'host': DEFAULT_HOST,
                'service': 'Node Exporter'
            },
            'targets': ['node-exporter:9100']
        }

        store_config(config_files, filename, config)


def generate_prometheus_target(service, config_files):

    config = None

    software_name = GITHUB_CLIENT_NAMES.get('prometheus', 'Prometheus')

    if service is None:
        config = {
            'labels': {
                'client': software_name,
                'service': 'Prometheus',
                'host': DEFAULT_HOST
            }
        }
    else:
        config = {
            'labels': {
                'client': 'prometheus',
                'host': service.get('host', DEFAULT_HOST),
                'service': service.get('service_name', 'Prometheus')
            }
        }

    # Make this configurable
    config['targets'] = ['prometheus:9090']

    store_config(config_files, 'prometheus.yml', config)


def generate_grafana_target(service, config_files):

    config = None

    software_name = GITHUB_CLIENT_NAMES.get('grafana', 'Grafana')

    if service is None:
        config = {
            'labels': {
                'client': software_name,
                'service': 'Grafana',
                'host': DEFAULT_HOST
            }
        }
    else:
        config = {
            'labels': {
                'client': software_name,
                'host': service.get('host', DEFAULT_HOST),
                'service': service.get('service_name', 'Grafana')
            }
        }

    # Make this configurable
    config['targets'] = ['grafana:3000']

    store_config(config_files, 'grafana.yml', config)


def generate_json_exporter_target(service, config_files):

    config = None

    software_name = GITHUB_CLIENT_NAMES.get('json-exporter', 'JSON Exporter')

    if service is None:
        config = {
            'labels': {
                'client': software_name,
                'service': 'json_exporter',
                'host': DEFAULT_HOST
            }
        }
    else:
        config = {
            'labels': {
                'client': software_name,
                'host': service.get('host', DEFAULT_HOST),
                'service': service.get('service_name', 'json_exporter')
            }
        }

    # Make this configurable
    config['targets'] = ['json-exporter:7979']

    store_config(config_files, 'json_exporter.yml', config)


def generate_fee_addresses_targets(group, addresses, config_files):

    execution_service = matching_record = next((service for service in group['services'] if service['service_type'] == SERVICE_TYPE_EXECUTION), None)

    software = execution_service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Execution Client')

    if execution_service is not None:
        config = {
            'labels': {
                'service': software_name,
                'instance': execution_service.get('api_address', ''),
                'explorer': group.get('execution explorer', DEFAULT_EXE_EXPLORER),
                'host': execution_service.get('host', DEFAULT_HOST),
                'network': group.get('network', DEFAULT_NETWORK),
                'group': group.get('group_name', DEFAULT_GROUP)
            },
            'targets': addresses
        }

        store_config(config_files, 'fee_addresses.yml', config)


def generate_validator_targets(group, addresses, config_files):

    consensus_service = matching_record = next((service for service in group['services'] if service['service_type'] == SERVICE_TYPE_CONSENSUS), None)

    software = consensus_service['software'].lower()
    software_name = GITHUB_CLIENT_NAMES.get(software, 'Consensus Client')

    if consensus_service is not None:
        config = {
            'labels': {
                'service': software_name,
                'instance': consensus_service.get('api_address', ''),
                'explorer': group.get('consensus explorer', DEFAULT_CON_EXPLORER),
                'host': consensus_service.get('host', DEFAULT_HOST),
                'network': group.get('network', DEFAULT_NETWORK),
                'group': group.get('group_name', DEFAULT_GROUP)
            },
            'targets': addresses
        }

        store_config(config_files, 'validators.yml', config)


def generate_currency_targets(currencies, config_files):

    if currencies is not None:
        currencies = [string.lower() for string in currencies]

        config = {
            'labels': {
                'source': 'CoinGecko'
            },
            'targets': [ ','.join(currencies) ]
        }

        store_config(config_files, 'currencies.yml', config)


def generate_github_targets(config_files):

    configs = [
        {'targets': ['ledgerwatch/erigon'], 'labels': {'client': 'Erigon'}},
        {'targets': ['nethermindeth/nethermind'], 'labels': {'client': 'Nethermind'}},
        {'targets': ['ethereum/go-ethereum'], 'labels': {'client': 'Geth'}},
        {'targets': ['hyperledger/besu'], 'labels': {'client': 'Besu'}},
        {'targets': ['prysmaticlabs/prysm'], 'labels': {'client': 'Prysm'}},
        {'targets': ['consensys/teku'], 'labels': {'client': 'Teku'}},
        {'targets': ['status-im/nimbus-eth2'], 'labels': {'client': 'Nimbus'}},
        {'targets': ['sigp/lighthouse'], 'labels': {'client': 'Lighthouse'}},
        {'targets': ['attestantio/dirk'], 'labels': {'client': 'Dirk'}},
        {'targets': ['attestantio/vouch'], 'labels': {'client': 'Vouch'}},
        {'targets': ['chainsafe/lodestar'], 'labels': {'client': 'Lodestar'}},
        {'targets': ['prometheus/prometheus'], 'labels': {'client': 'Prometheus'}},
        {'targets': ['prometheus/node_exporter'], 'labels': {'client': 'Node Exporter'}},
        {'targets': ['prometheus/blackbox_exporter'], 'labels': {'client': 'Blackbox Exporter'}},
        {'targets': ['prometheus-community/json_exporter'], 'labels': {'client': 'JSON Exporter'}},
        {'targets': ['ethpandaops/ethereum-metrics-exporter'], 'labels': {'client': 'Ethereum Metrics Exporter'}},
        {'targets': ['grafana/grafana'], 'labels': {'client': 'Grafana'}}
    ]

    for config in configs:
        store_config(config_files, 'github.yml', config)


def generate_blackbox_exporter_target(service, config_files):

    software_name = GITHUB_CLIENT_NAMES.get('blackbox-exporter', 'Blackbox Exporter')

    if service is not None:
        config = {
            'labels': {
                'client': software_name,
                'host': service.get('host', DEFAULT_HOST),
                'service': service.get('service_name', 'blackbox_exporter')
            }
        }

        # Make this configurable
        config['targets'] = ['blackbox-exporter:9115']

        store_config(config_files, 'blackbox_exporter.yml', config)


def generate_ethereum_metrics_exporter_targets(group, service, config_files):

    config = None
    filename = None
    local_used = False

    software_name = GITHUB_CLIENT_NAMES.get('ethereum-metrics-exporter', 'Ethereum Metrics Exporter')

    if service is None:

        config = {
            'labels': {
                'group': DEFAULT_GROUP,
                'host': DEFAULT_HOST,
                'network': DEFAULT_NETWORK,
                'service': 'Ethereum Metrics Exporter',
                'client': software_name
            },
            'targets': ['ethereum-metrics-exporter:9095']
        }
        local_used = True

    else:

        config = {
            'labels': {
                'service': service.get('service_name', 'Ethereum Metrics Exporter'),
                'host': service.get('host', DEFAULT_HOST),
                'network': group.get('network', DEFAULT_NETWORK),
                'group': group.get('group_name', DEFAULT_GROUP),
                'client': software_name
            },
        }

        if 'metrics_address' in service:
            config['targets'] = [service['metrics_address']]
        else:
            config['targets'] = ['ethereum-metrics-exporter:9095']
            local_used = True

    # We can only have a single target that uses the local instance.
    if local_used:
        filename = 'ethereum-metrics-exporter.yml'
        if filename in config_files:
            print('Ethereum Metrics Exporter container already in use. Specify "metrics_api" for additional Ethereum Metrics Exporter instances.')
        else:
            store_config(config_files, filename, config)
    else:
        filename = 'ethereum-metrics-exporter-external.yml'
        store_config(config_files, filename, config)


# Generates one or more configuration files for the Ethereum Metrics Exporter
# client itself. Not for Prometheus. Will only generate a single config
# file for the Ethereum Metrics Exporter instance internal to the environment.
# additional instances must be run externally and IP addresses explicitly
# specified.
def generate_ethereum_metrics_exporter_configurations(data):

    config_files = {}

    for group in data['staking_groups']:

        ethereum_metrics_exporter_service = matching_record = next((service for service in group['services'] if service['service_type'] == SERVICE_TYPE_BLACKBOX_EXPORTER), None)
        consensus_service = matching_record = next((service for service in group['services'] if service['service_type'] == SERVICE_TYPE_CONSENSUS), None)
        execution_service = matching_record = next((service for service in group['services'] if service['service_type'] == SERVICE_TYPE_EXECUTION), None)

        config = {}
        clients = 0

        if consensus_service is not None and 'api_address' in consensus_service:
            clients += 1

            if 'software' in consensus_service and consensus_service['software'] is not None:
                name = GITHUB_CLIENT_NAMES[consensus_service['software'].lower()]
            else:
                name = 'Consensus Client'

            config['consensus'] = {
                'enabled': True,
                'url': 'http://' + consensus_service['api_address'],
                'name': name
            }

        if execution_service is not None and 'api_address' in execution_service:
            clients += 1

            if 'software' in execution_service and execution_service['software'] is not None:
                name = GITHUB_CLIENT_NAMES[execution_service['software'].lower()]
            else:
                name = 'Execution Client'

            config['execution'] = {
                'enabled': True,
                'url': 'http://' + execution_service['api_address'],
                'name': name,
                'modules': ['eth', 'net', 'web3', 'txpool']
            }

            if clients == 2:
                config['pair'] = {'enabled': True}

            if 'ethereum-metrics-exporter.yml' not in config_files:
                filename = 'ethereum-metrics-exporter.yml'
            else:
                filename = create_filename('ethereum-metrics-exporter-', group.get('group_name', DEFAULT_GROUP), '.yml')

            # No point in saving a file without at least one client.
            if clients > 0:
                store_config(config_files, filename, config)

    return config_files


