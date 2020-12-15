# Netsage Flow Collectors

This repository hosts all the code related to data collection.  Currently 
encompasing the sflow and netflow data and be expanded.

External Dependency:
  - A rabbitMQ instance is required with the following queues created:
      - netflow_queue
      - sflow_queue


This project is current in an alpha stage:

Tools used:
  - [pmacct](https://github.com/pmacct/pmacct) is used primarily for the data collection.
  - [iperf3](https://software.es.net/iperf/) is used to generate sflow data for testing.
  - [host-sflow](https://github.com/sflow/host-sflow) is used to collect data on the host and retransmite to the pmacct receiver