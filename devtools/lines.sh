#!/bin/bash

script_dir=$(dirname $(realpath "${BASH_SOURCE[0]}"))
parent_dir=$(dirname "${script_dir}")

wc -l $(fdfind .py "${parent_dir}")
