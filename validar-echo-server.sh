#!/bin/bash

echo "Starting echo server test..."
TEST_MESSAGE="test_message"
NETWORK_NAME=$(docker network ls --format "{{.Name}}" | grep -vE "bridge|host|none" | head -1)
if [[ -n "$NETWORK_NAME" ]]; then
    echo "Using existing network: $NETWORK_NAME"
else
    NETWORK_NAME="generator_network"
    docker network create $NETWORK_NAME
    echo "Created new network: $NETWORK_NAME"
fi
RESPONSE=$(docker run --rm --network $NETWORK_NAME \
    alpine /bin/sh -c "echo '$TEST_MESSAGE' | nc server 12345")

if [ "$TEST_MESSAGE" == "$RESPONSE" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi

echo "Test completed."