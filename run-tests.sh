#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Usage:
#   ./run-tests.sh [-K|--keep-services] [pytest options and args...]
#
# Note: the DB, SEARCH and MQ services to use are determined by corresponding environment
#       variables if they are set -- otherwise, the following defaults are used:
#       SEARCH=opensearch
#
# Example for using mysql instead of postgresql:
#    DB=mysql ./run-tests.sh

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Define function for bringing down services
function cleanup {
  eval "$(docker-services-cli down --env)"
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
pytest_args=()
for arg in $@; do
	# from the CLI args, filter out some known values and forward the rest to "pytest"
	# note: we don't use "getopts" here b/c of some limitations (e.g. long options),
	#       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
	case ${arg} in
		-K|--keep-services)
			keep_services=1
			;;
		*)
			pytest_args+=( ${arg} )
			;;
	esac
done

if [[ ${keep_services} -eq 0 ]]; then
	trap cleanup EXIT
fi

export LC_TIME=en_US.UTF-8
python -m check_manifest
python -m sphinx.cmd.build -qnNW docs docs/_build/html
eval "$(docker-services-cli up --search ${SEARCH:-opensearch} --env)"
# Note: expansion of pytest_args looks like below to not cause an unbound
# variable error when 1) "nounset" and 2) the array is empty.
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
tests_exit_code=$?
exit "$tests_exit_code"