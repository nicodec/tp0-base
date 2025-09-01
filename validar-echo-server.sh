#!/bin/bash

echo "Starting echo server test..."
TEST_MESSAGE="test_message"
RESPONSE=$(docker run --rm --network generator_network \
    alpine /bin/sh -c "echo '$TEST_MESSAGE' | nc server 12345")

if [ "$TEST_MESSAGE" == "$RESPONSE" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi

echo "Test completed."