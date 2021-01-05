## Docker Flow

## Running container


Assuming default configuration, the files are all created in the `deploy` folder.  We'll assume you're inside that directroy to issue any of these commands.

```
## Bringing up container
docker-compose up -d 
## Viewing logs
docker-compose logs -f 
```

Once the collector is up, you'll need to configure the appropriate routers to send metrics 
to the appropriate ip/port combination via UDP.


