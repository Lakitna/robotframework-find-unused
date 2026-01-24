#!/usr/bin/env bash

# File to run inside the gif builder Docker image. Project root at `/app`

# Bail early
set -e

########################

cd /app/test/projects/tilavarauspalvelu-robot

vhs /app/docs/gif/arguments/arguments.tape
vhs /app/docs/gif/files/files.tape
vhs /app/docs/gif/keywords/keywords.tape
vhs /app/docs/gif/returns/returns.tape
vhs /app/docs/gif/variables/variables.tape
