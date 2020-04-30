
# txm-s3-log-shipper-lambda

This is an AWS Lambda for shipping logs from S3 into our telemetry stack.

## How and why?

In some cases, logs are written into S3 where we don't have a custom AMI to inject logstash, for example.

In such cases, this lamba can be deployed and hooked up to an S3 PUT event on the logging bucket. Then,

* The lambda is alerted to the S3 event.
* If checks if it has a parser configured for log files at that path.
* It retrieves the file (or gzipped) file as stream from the S3 bucket.
* It parses the logs and the log path according to the configured grok rules.
* It standardises the timestamps and writes the JSON into elasticache (redis).
* The logs are then indexed by elasticsearch and available in Kibana.

### License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
