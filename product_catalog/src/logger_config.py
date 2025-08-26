import os
from dotenv import load_dotenv
import yaml
import logging.config
import time

load_dotenv()

# Ensure log directory exists
log_dir = os.environ.get('LOG_DIR', '/var/log/default_service')
os.makedirs(log_dir, exist_ok=True)

def setup_logging(
    default_path='src/logging_config.yaml',
    default_level=logging.DEBUG,
    env_key='LOG_CFG'
):
    path = os.getenv(env_key, default_path)
    if path and not path.endswith('.yaml'):
        path += '.yaml'

    if path:
        print(f"Loading logging config from: {path}")

    try:
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config_text = f.read()
        # Substitute environment variables
            config_text = config_text.replace('${SERVICE_NAME}', os.environ.get('SERVICE_NAME', 'default_service'))
            config_text = config_text.replace('${LOG_DIR}', os.environ.get('LOG_DIR', '/var/log/default_service'))
            config = yaml.safe_load(config_text)
            logging.config.dictConfig(config)
            logging.Formatter.converter = time.localtime
        else:
            raise FileNotFoundError(f"Logging config file not found at path: {path}")
    except Exception as e:
        print(f"Error loading logging configuration: {e}. Using basicConfig.")
        logging.basicConfig(level=default_level)

setup_logging()
logger = logging.getLogger(os.environ.get('SERVICE_NAME', 'default_service'))

service_name = os.environ.get('SERVICE_NAME', 'default_service')
logger.info(f"{service_name} logger initialized.")

