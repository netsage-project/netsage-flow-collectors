from loguru import logger
from gen_lib.config import Config
import os
import shutil
from jinja2 import Environment, PackageLoader, select_autoescape, Template, FileSystemLoader
import gila
from pathlib import Path


class Process(object):
    def __init__(self):
        self.config = Config.instance()
        self.file_loader = FileSystemLoader(self.config.template_folder)
        self.env = Environment(loader=self.file_loader)

    def clean(self):
        if os.path.exists(self.config.deploy_path):
            logger.info("Removing all files in deploy directory: {}".format(self.config.deploy_path))
            try:
                shutil.rmtree(self.config.deploy_path)
            except OSError as e:
                logger.error("Failed to delete deployment directory: {}".format(self.config.deploy_path))

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
        output = os.path.join(self.config.deploy_path, ".env")
        self.render_template("docker/env.example", output, {"dev_queue": self.config.dev_queue})
        # src = self.config.template_path("docker", self.config.environment)
        # shutil.copyfile(src, env_out)
        # logger.info("Copying .env file to deploy directory")

    def __generate_docker__(self):
        self.__generate_environment__()
        logger.info("Generating docker files")
        sensors = self.config.sensors
        data = {"netflow_sensors": sensors.netflow_sensors, "sflow_sensors": sensors.sflow_sensors,
                "production": not self.config.dev_queue}

        output = os.path.join(self.config.deploy_path, "docker-compose.yml")
        self.render_template("docker/docker-compose.yml", output, data)

        if self.config.dev_generate or self.config.dev_queue:
            self.__generate_docker__dev__(sensors)

    def render_template(self, template_name, output, data):
        template = self.env.get_template(template_name)
        dirname = os.path.dirname(output)
        if not os.path.exists(dirname):
            p = Path(dirname)
            p.mkdir(parents=True)
        raw_output = template.render(data)
        with open(output, 'w') as writer:
            writer.write(raw_output)

    def __generate_pmacct__(self):
        sensors = self.config.sensors
        for item in sensors.sflow_sensors:
            sflow_config = {"pmacctd_type": "sfacctd", "port": "9997", "queue_name": "sflow"}
            sflow_config["sensorName"] = item.name
            sflow_config["instanceName"] = item.instance
            output = os.path.join(self.config.deploy_path, "conf", "sflow", item.name, "sfacctd.conf")
            self.render_template("pmacct.conf", output, sflow_config)
            output = output.replace("sfacctd.conf", "pretag.map")
            self.render_template("pretag.map", output, sflow_config)
        for item in sensors.netflow_sensors:
            netflow_config = {"pmacctd_type": "nfacctd", "port": "9996","queue_name": "netflow" }
            netflow_config["sensorName"] = item.name
            netflow_config["instanceName"] = item.instance
            output = os.path.join(self.config.deploy_path, "conf", "netflow", item.name, "nfacctd.conf")
            self.render_template("pmacct.conf", output, netflow_config)
            output = output.replace("nfacctd.conf", "pretag.map")
            self.render_template("pretag.map", output, netflow_config)

    def __generate_docker__dev__(self, sensors):
        logger.info("Generating docker Dev files")
        output = os.path.join(self.config.deploy_path, "docker-compose.override.yml")
        data = {"netflow_sensors": sensors.netflow_sensors, "sflow_sensors": sensors.sflow_sensors,
                "dev_queue": self.config.dev_queue, "generate": self.config.dev_generate}

        self.render_template("docker/docker-compose.override_example.yml", output, data)

    def run(self):
        self.__sanity_checks__()
        self.__generate_docker__()
        self.__generate_pmacct__()
