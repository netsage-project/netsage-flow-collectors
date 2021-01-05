# Netsage Flow Collector

This project is intended to faciliate the data collection of various types of flows and deliver the data to a message queue.  Currently utilizing RabbitMQ but any message queue that [pmacct](https://github.com/pmacct/pmacct) can use would work.

## Notes
More detailed documentation will eventually live at: https://netsage-project.github.io/netsage-pipeline/docs/pipeline/intro/.




## Installation

### Installation Notes:

You can run this via a docker stack (recommended) or using a baremetal install.  If you choose to use a bare metal install you need to 


Install the dependencies:

```sh
pip install -r requirements.txt
```

copy the default configuration and update according to your environment.

```sh
cp gen_config/collectors.template.yml  gen_config/collectors.yml 
```

The default is for the configuration to be created under `deploy` folder.  It'll create two sensors.


The default behavior is to support 1 netflow and 1 sflow collector.  We're assuming you'll be running in production mode.

For Developers please consider setting include_dev_generate and include_dev_queue to true.

At this point please select one of the following:

  * [Docker](02_docker_install.md) Flow
  * [BareMetal](03_baremetal.md) Server Install

