# Netsage Flow Collector

This project is intended to faciliate the data collection of various types of flows and deliver the data to a message queue.  Currently utilizing RabbitMQ but any message queue that [pmacct](https://github.com/pmacct/pmacct) can use would work.

## Notes

Recommended Deployment:
  - Ideally the collectors are all running on a single host.  This does not need to be the case as long the message bus is accessible, but you would have to manually ensure 

This repo is somewhat geared more towards a docker deployment, but a bare metal install is doable.  It does assume that the collectors are all running on a single host.  