#!/usr/bin/env bash

export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

readonly basedir="$(dirname "$0")"
cd $basedir
pipenv run ./notify_book_availability.py "$@"
