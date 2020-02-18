# python_loki_exporter
Export metrics from loki to prometheus

## usage:
docker build -t app .
docker run -it app python3 main.py -f config.json

```json config.json
{
"loki_host": "http://localhost:3100",
"server_port": 8779,
"timeout": 10,
"metrics":{
  "labels": true,
  "label_values": true,
  "queries": true
},
"queris": [
    {
        "q": "count_over_time({filename=\"/var/log/auth.log\"} |=\"CRON\"[5m])",
        "name": "loki_metric_cron_5m",
        "description": "Count of cron name in logs for 5 minutes"
    },
    {
        "q": "count_over_time({filename=\"/var/log/auth.log\"} |=\"CRON\"[15m])",
        "name": "loki_metric_cron_15m"
    }
]
}
```