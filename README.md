# home-monitoring
Containerized Home monitoring solution (server python + Influxdb + grafana) 


> launch the server + grafana + influxdb

```shell
 docker-compose up
```


> rebuild the temp-server image only
```shell
 docker-compose up --build --force-recreate --no-deps temp-server
```
