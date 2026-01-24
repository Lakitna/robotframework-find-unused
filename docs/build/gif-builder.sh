#!/usr/bin/env bash

# Bail early
set -e
# CD to this script dir
cd "$(dirname "$0")"

########################

cd ../gif

vhs ./arguments/arguments.tape
vhs ./files/files.tape
vhs ./keywords/keywords.tape
vhs ./returns/returns.tape
vhs ./variables/variables.tape
