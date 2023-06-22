from lib.processors.processor_v1_0 import process_data_v1_0

def process_data(data, prompath=None, emepath=None):
    version = data.get('version')

    if version == '1.0':
        return process_data_v1_0(data, prompath, emepath)
    else:
        raise ValueError(f"Unsupported version: {version}")
