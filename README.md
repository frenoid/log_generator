# Supermarket log generator
Generates simulated logs from a websever running a supermarket website <br>
Used in the blog article [Set up a Kafka cluster on Amazon EC2](https://normanlimxk.com/2021/11/01/setup-a-kafka-cluster-on-amazon-ec2/) as a mock data source.
### Start producing logs
`source make_logs.sh`
### See the generated logs
`source follow_logs.sh`
### Stop the log generation
`source cease_logs.sh`
### Reset the log file
`source replace_logs.sh`
