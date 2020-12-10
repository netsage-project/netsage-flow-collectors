echo "Warning: You need the Dev containers to be running for this to work"
echo "agent and iperf3 server are required"

docker run --rm sflow/iperf3 -c host.docker.internal
