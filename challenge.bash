#!/bin/bash

TOP_DIR=$(dirname $(readlink -f ${0}))

_challenge_compose() {
    local challenge="${1}"
    shift
    local args="${*}"
    pushd ${TOP_DIR}/${challenge}
    docker-compose -f ../common/docker-compose.yml ${args}
    popd
}

build_service() {
    local challenge="${1}"
    echo "Build challenge service"
    _challenge_compose ${challenge} down
    _challenge_compose ${challenge} build
}

start_challenge_service() {
    local challenge="${1}"
    _challenge_compose ${challenge} down
    _challenge_compose ${challenge} up -d
}

start_hack() {
    local challenge="${1}"
    pushd ${TOP_DIR}
    PYTHONPATH=. python ${challenge}/hack.py
    popd
}

CHALLENGE="${1}"
build_service "${CHALLENGE}"
start_challenge_service "${CHALLENGE}"
echo "Wait..."
sleep 5
echo "Start hack"
start_hack "${CHALLENGE}"
