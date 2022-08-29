#!/usr/bin/env bash

readonly basedir="$(dirname "$0")"
cd $basedir
pipenv run ./notify_book_availability.py "$@"
