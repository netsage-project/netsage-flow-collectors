from loguru import logger
from gen_lib.config import Config
import os
import shutil
from jinja2 import Environment, PackageLoader, select_autoescape, Template, FileSystemLoader
import gila


class Process(object):
    def __init__(self):
        self.config = Config.instance()
        self.file_loader = FileSystemLoader(self.config.template_folder)
        self.env = Environment(loader=self.file_loader)

    def __sanity_checks__(self):
        sflow_path = os.path.join(self.config.deploy_path, "conf", "sflow")
        netflow_path = os.path.join(self.config.deploy_path, "conf", "netflow")
        for path in [self.config.deploy_path, sflow_path, netflow_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    logger.info("Created directory '{}'".format(path))
                except:
                    raise Exception("Destination folder does not exist and cannot be created")

    def __generate_environment__(self):
        src = self.config.template_path("docker", self.config.environment)
        env_out = os.path.join(self.config.deploy_path, ".env")
        shutil.copyfile(src, env_out)
        logger.info("Copying .env file to deploy directory")

    def __generate_docker__(self):
        self.__generate_environment__()
        # compose_template = self.env.get_template("docker/samir.txt")
        compose_template = self.env.get_template("docker/docker-compose.yml")
        s = self.config.sensors

        raw_output = compose_template.render(netflow_sensors=s.netflow_sensors, sflow_sensors=s.sflow_sensors,
                                             production=not self.config.dev_mode)
        output = os.path.join(self.config.deploy_path, "docker-compose.yml")
        with open(output, 'w') as writer:
            writer.write(raw_output)
            # self.config.template_path("docker", "docker-compose.yml")

        logger.info("Generating docker files")
        if self.config.dev_mode:
            self.__generate_docker__dev__()

    def __generate_pmacct__(self):
        logger.info("Generating pm account files")

    def __generate_docker__dev__(self):
        logger.info("Generating docker Dev files")

    def run(self):
        self.__sanity_checks__()
        self.__generate_docker__()
        self.__generate_pmacct__()
