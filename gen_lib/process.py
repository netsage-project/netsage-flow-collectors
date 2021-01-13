from loguru import logger
from gen_lib.config import Config
import os
import shutil
from jinja2 import (
    Environment,
    PackageLoader,
    select_autoescape,
    Template,
    FileSystemLoader,
)
import gila
from pathlib import Path


class Process(object):
    def __init__(self):
        self.config = Config.instance()
        self.file_loader = FileSystemLoader(self.config.template_folder)
        self.env = Environment(loader=self.file_loader)

    def clean(self):
        """
        Will delete all the generated and volume data in the deploy destination
        """
        if os.path.exists(self.config.deploy_path):
            logger.info(
                "Removing all files in deploy directory: {}".format(
                    self.config.deploy_path
                )
            )
            try:
                shutil.rmtree(self.config.deploy_path)
            except OSError as e:
                logger.error(
                    "Failed to delete deployment directory: {}".format(
                        self.config.deploy_path
                    )
                )

    def __sanity_checks__(self):
        """
        Ensures all config base paths and deployment directory exist
        """
        sflow_path = os.path.join(self.config.deploy_path, "conf", "sflow")
        netflow_path = os.path.join(self.config.deploy_path, "conf", "netflow")
        for path in [self.config.deploy_path, sflow_path, netflow_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    logger.info("Created directory '{}'".format(path))
                except:
                    raise Exception(
                        "Destination folder does not exist and cannot be created"
                    )

    def __generate_environment__(self):
        """
        Configures Environment file based on app config and creates a .env file
        """
        output = os.path.join(self.config.deploy_path, ".env")
        data = {"dev_queue": self.config.dev_queue}
        config = Config.instance()
        rabbit = config.pmacct_config.rabbit.get_dict()
        data.update(rabbit)
        self.__render_template__("docker/env.example", output, data)

    def __generate_docker__(self):
        """
        Generates docker-compose file and invokes environment file creation
        """
        self.__generate_environment__()
        logger.info("Generating docker files")
        sensors = self.config.sensors
        data = {
            "netflow_sensors": sensors.netflow_sensors,
            "sflow_sensors": sensors.sflow_sensors,
            "production": not self.config.dev_queue,
        }

        output = os.path.join(self.config.deploy_path, "docker-compose.yml")
        self.__render_template__("docker/docker-compose.yml", output, data)

        if self.config.dev_generate or self.config.dev_queue:
            self.__generate_docker__dev__(sensors)

    def __render_template__(self, template_name, output, data):
        """
        Helper Utility that will generate a file and inject required
        data into the final output
        """
        template = self.env.get_template(template_name)
        dirname = os.path.dirname(output)
        if not os.path.exists(dirname):
            p = Path(dirname)
            p.mkdir(parents=True)
        raw_output = template.render(**data)
        with open(output, "w") as writer:
            writer.write(raw_output)

    def __generate_pmacct__(self):
        """
        Generates the configuration files and pretag mapping for netflow/sflow tooling
        """
        sensors = self.config.sensors
        pmconfig = self.config.pmacct_config
        for item in sensors.sflow_sensors:
            sflow_config = pmconfig.sflow_config
            sflow_config.update(pmconfig.rabbit.get_dict())
            sflow_config["sensorName"] = item.name
            sflow_config["instanceID"] = item.instance
            output = os.path.join(
                self.config.deploy_path,
                "conf",
                "sflow",
                item.name,
                sflow_config.get("pmacctd_type"),
            )
            self.__render_template__("pmacct.conf", output, sflow_config)
            output = output.replace(sflow_config.get("pmacctd_type"), "pretag.map")
            self.__render_template__("pretag.map", output, sflow_config)
        for item in sensors.netflow_sensors:
            netflow_config = pmconfig.netflow_config
            netflow_config["sensorName"] = item.name
            netflow_config["instanceID"] = item.instance
            netflow_config.update(pmconfig.rabbit.get_dict())
            output = os.path.join(
                self.config.deploy_path,
                "conf",
                "netflow",
                item.name,
                netflow_config.get("pmacctd_type"),
            )
            self.__render_template__("pmacct.conf", output, netflow_config)
            output = output.replace(netflow_config.get("pmacctd_type"), "pretag.map")
            self.__render_template__("pretag.map", output, netflow_config)

    def __generate_docker__dev__(self, sensors):
        """
        Generate the docker over file if invoked.
        """
        logger.info("Generating docker Dev files")
        output = os.path.join(self.config.deploy_path, "docker-compose.override.yml")
        data = {
            "netflow_sensors": sensors.netflow_sensors,
            "sflow_sensors": sensors.sflow_sensors,
            "dev_queue": self.config.dev_queue,
            "generate": self.config.dev_generate,
        }

        self.__render_template__(
            "docker/docker-compose.override_example.yml", output, data
        )

    def run(self):
        """
        Entry point that creates all the docker, pmaccount and environment files
        necessery.
        """
        self.__sanity_checks__()
        self.__generate_docker__()
        self.__generate_pmacct__()
