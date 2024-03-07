#!/usr/bin/env bash

set -eux

apk add go
pushd collections/ansible_collections/foo/bar/plugins/modules
go build -o "helloworld_$(go env GOOS)_$(go env GOARCH)" helloworld.go
popd
ANSIBLE_COLLECTIONS_PATH="${PWD}/collections:${ANSIBLE_COLLECTIONS_PATH}" ansible-playbook playbook.yml "$@"
