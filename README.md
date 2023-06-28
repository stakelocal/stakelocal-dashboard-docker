# Stake Local Dashboard Docker

## Introduction

The Stake Local Dashboard Docker project provides an easier method of deploying the Stake Local Dashboard using Docker. For single consensus/execution client pairs, the setup process involves three steps:

1. Create a configuration file describing your node architecture. Examples are provided.
2. Run a Python script to convert the configuration file to the necessary Prometheus targets and Ethereum Metrics Exporter configuration files.
3. Run `docker-compose`

You could be running the Stake Local Dashboard in 5 minutes.

## Motivation

The Stake Local Dashboard uses Grafana and Prometheus to collect and display Ethereum staking data from five Ethereum consensus clients, four Ethereum execution clients, three Ethereum validator clients, node_exporter, json_exporter, Ethereum Metrics Exports, GitHub, and CoinGecko. It also supports monitoring of multiple consensus/execution pairs using a single Docker compose app.* For best results, the labels applied to data stored by Prometheus must be properly assigned, and there are many targets across which labels must be coordinated.

The Stake Local Dashboard Docker project was created to simplify this process.

**If you are running services across multiple hosts and would like to see node_exporter data from more than one hosts, you will need to run additional stand-alone node_exporter instances on each host. If you are running multiple consensus/execution clients, you will need to run additional Ethereum Metrics Exporter instances for each group. The Stake Local Dashboard Docker supports running a single instance of node_exporter and Ethereum Metrics Exporter (for now). These can be used for one host and one group. All others will require separate instances.*

## Configuration

### Clone the Repository

```bash
git clone https://github.com/stakelocal/stakelocal-dashboard-docker
```

### Create Configuration File

Enter the stakelocal-dashboard-docker folder and copy one of the example configuration files from the example_configs folder. Here we are using the `recommended_config.yml`. If you want to save a few minutes you can start with `minimal_mainnet_config.yml` , but if you like the dashboard, you will likely want some of the additional features provided by the recommended configuration.

Other example configuration files provided include:

- `minimal_goerli_config.yml` - A minimal configuration to get you up and running on the Goerli network quickly.
- `multi_group_config.yml` - A maximal configuration supporting multiple consensus/execution client groups running on multiple hosts. Includes support for external stand-alone node_exporter and Ethereum Metrics Exporter instances while using the docker internal instances for a single group.
- `eth-docker_config.yml` - A configuration for running the Stake Local Dashboard docker application alongside eth-docker. 
- `rocketpool_config.yml` - A configuration for running the Stake Local Dashboar docker application alongside RocketPool.

```bash
cd stakelocal-dashboard-docker
cp example_configs/recommended_config.yml ./custom_config.yml
```

Edit the `custom_config.yml` and make changes based on one of the following sections.

```bash
nano custom_config.yml
```

Modify the following values, as needed:

- **group_name** - The name you use to distinguish one consensus/execution pair from another. You will select this from a menu in the dashboard to switch between groups. For example, "Goerli Lighthouse/Besu".
- **network** - The name of the network to which you are connecting. For example, "Mainnet". This is for display purposes only. Any network name will work.
- **services** - For each service in the `services` section, modify the following:
  - **software** - For `consensus` service_type, this must be `lighthouse`, `lodestar`, `nimbus`, `prysm`, or `teku`. For `execution` service type, this must be `besu`, `erigon`, `geth`, or `nethermind`. For validator service_type, this must be  `lighthouse`, `lodestar`, or `prysm`.
  - **host** - The name you use to distinguish one server or VM from another. You will select this from a menu in the dashboard to switch between hosts for node_exporter data. For example: "server-name".
  - **metrics_address** and **api_address** - The IP address and port at which the metrics and API methods may be accessed. The IP address must be a LAN address or docker service name and not a loopback address (127.0.0.1, localhost).
    - **RocketPool and eth-docker:** Leave these values unchanged from the values set in the example configuration files. These values are configured to support their specific docker service names and ports.
    - Validator clients do not require an `api_address` value.
- **consensus_explorer** - The domain name to beaconcha.in for the correct network. For example: "goerli.beaconcha.in".
- **execution_explorer** - The domain name to etherscan.io for the correct network. For example: "goerli.etherscan.io".
- **validators** - The indices or addresses of your validators. This information is used for validator balances. Validator addresses must be in quotes, single or double. Validator indices do not need to be quoted.
- **fee_addresses** - Ethereum addresses for any configured fee addresses. This information is used for fee address balances. Fee addresses must be in quotes, single or double.
- **shared_services** - For each service in the `shared_services` section, modify the following:
  - **host** - The name you use to distinguish one server or VM from another. You will select this from a menu in the dashboard to switch between hosts for software data. This should be the name of the server of VM on which the docker app is running.

Save and exit the editor.

### Generate Prometheus Targets and Configuration Files

Run the following command to read in your `custom_config.yml` file and generate the Prometheus target files and other configuration files used for dashboard operation.

```bash
python3 stakelocal_config.py custom_config.yml
```

You should see output similar to the following:

```bash
./compose/prometheus/files_sd/con_api_lighthouse.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/con_metrics_lighthouse.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/val_metrics_lighthouse.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/exe_api_besu.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/exe_metrics_besu.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/fee_addresses.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/validators.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/ethereum-metrics-exporter.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/grafana.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/prometheus.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/json_exporter.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/node_exporter.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/currencies.yml generated successfully with 1 entries.
./compose/prometheus/files_sd/github.yml generated successfully with 17 entries.
./compose/etheruem-metrics-exporter/ethereum-metrics-exporter.yml generated successfully with 1 entries.
Configuration completed successfully.
```

Configuration is complete.

### RocketPool and eth-docker Environment Configuration

RocketPool and eth-docker monitoring will require access to the network internal to RocketPool and eth-docker applications. This can be configured in the `.env` file. Pre-configured `.env` files have been provided for both RocketPool and eth-docker. Copy the appropriate file over the `compose/.env` file.

For RocketPool:

```bash
cp compose/.env.rocketpool compose/.env
```

For eth-docker:

```bash
cp compose/.env.eth-docker compose/.env
```

### Configure Firewall

Make sure that port 3003 is open on your server, this is the port at which you can access the Grafana dashboard. 

If you are running `ufw`, run the following command.

```bash
sudo ufw allow 3003/tcp
```

You do not need to open port 9003 on your router.

### Run Stake Local Dashboard Docker

To start the dashboard, run the following command:

```bash
sudo docker compose -f compose/docker-compose.yml -p stakelocal up --detach
```

Access the dashboard at: http://XXX.XXX.XXX.XXX:3003, where `XXX.XXX.XXX.XXX` is the IP address of the system on which docker is running.

While most data on the dashboard will appear immediately, some data may take additional time to appear.

- Latest GitHub release may take up to 30 minutes to appear.
- Annualized rates of change for addresses may take an epoch, an hour, or
  a day to appear, based on the time period represented.
- Validator data provided by the Prysm validator client may take an epoch to
  appear.

### Stop Stake Local Dashboard Docker

```bash
sudo docker compose -f compose/docker-compose.yml -p stakelocal down
```

## Notes

- Some data points reset after the source client has been restarted. For example, proposal data for individual validators and the total number of proposals will reset after the Prysm client is restarted.
- RocketPool and eth-docker both run their own instances of Prometheus, Grafana, and other monitoring utilities. Running this application alongside either of those will result in two copies of these applications running at the same time. This is a first attempt at integrating this dashboard with these applications and solutions may be found later to avoid duplication of processes.
