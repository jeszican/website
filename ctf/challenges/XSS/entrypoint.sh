#!/bin/bash

set -e

exec python3 caller.py &
exec python3 app.py