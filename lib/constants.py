DEFAULT_GROUP = 'Default Group'
DEFAULT_HOST = 'Default Host'
DEFAULT_NETWORK = 'Mainnet'
DEFAULT_CON_EXPLORER = 'beaconcha.in'
DEFAULT_EXE_EXPLORER = 'etherscan.io'

DEFAULT_CURRENCIES = [ 'USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'NZD', 'ILS', 'KRW', 'MXN', 'RUB', 'SGD', 'TWD', 'INR' ]

# Must be lower-case
CONSENSUS_CLIENTS = [ 'lighthouse', 'lodestar', 'nimbus', 'prysm', 'teku' ]
EXECUTION_CLIENTS = [ 'besu', 'erigon', 'geth', 'nethermind' ]

# How GitHub reports client names for each client.
GITHUB_CLIENT_NAMES = {
                        'besu': 'Besu',
                        'blackbox-exporter': 'Blackbox Exporter',
                        'dirk': 'Dirk',
                        'erigon': 'Erigon',
                        'ethereum-metrics-exporter': 'Ethereum Metrics Exporter',
                        'geth': 'Geth',
                        'grafana': 'Grafana',
                        'json-exporter': 'JSON Exporter',
                        'lighthouse': 'Lighthouse',
                        'lodestar': 'Lodestar',
                        'nethermind': 'Nethermind',
                        'nimbus': 'Nimbus',
                        'node-exporter': 'Node Exporter',
                        'prometheus': 'Prometheus',
                        'prysm': 'Prysm',
                        'teku': 'Teku',
                        'vouch': 'Vouch'
                      }

SERVICE_TYPE_VALIDATOR = 'validator'
SERVICE_TYPE_CONSENSUS = 'consensus'
SERVICE_TYPE_EXECUTION = 'execution'
SERVICE_TYPE_JSON_EXPORTER = 'json_exporter'
SERVICE_TYPE_GRAFANA = 'grafana'
SERVICE_TYPE_PROMETHEUS = 'prometheus'
SERVICE_TYPE_NODE_EXPORTER = 'node_exporter'
SERVICE_TYPE_BLACKBOX_EXPORTER = 'blackbox_exporter'
SERVICE_TYPE_ETH_METRICS = 'ethereum_metrics_exporter'

DOCKER_SERVICE_NAME_GRAFANA = 'sl-grafana'
DOCKER_SERVICE_NAME_PROMETHEUS = 'sl-prometheus'
DOCKER_SERVICE_NAME_NODE_EXPORTER = 'sl-node-exporter'
DOCKER_SERVICE_NAME_JSON_EXPORTER = 'sl-json-exporter'
DOCKER_SERVICE_NAME_ETHEREUM_METRICS_EXPORTER = 'sl-ethereum-metrics-exporter'
DOCKER_SERVICE_NAME_BLACKBOX_EXPORTER = 'sl-blackbox-exporter'

