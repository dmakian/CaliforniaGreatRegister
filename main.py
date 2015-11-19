import logging, os
from logging import config
import page_processor
from page_processor import Page, AlamedaPageProcessor
import yaml

def setup_logging(
    default_path='logging.yaml', 
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == '__main__':
	setup_logging()
	logger = logging.getLogger(__name__)
	logger.info('starting main task')
	page_processor.run()
	logger.info('ended main task')
