.PHONY: clean

clean:
	rm -f compose/ethereum-metrics-exporter/*
	rm -f compose/prometheus/files_sd/*
	rm -rf lib/__pycache__/
	rm -rf lib/processors/__pycache__/
