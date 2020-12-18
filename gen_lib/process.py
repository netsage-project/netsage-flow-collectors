from loguru import logger


class Process(object):
    def __init__(self):
        logger.info("woot")
    def run(self):
        logger.info("run")
