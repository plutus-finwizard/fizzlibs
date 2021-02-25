#!/bin/bash
  
# turn on bash's job control
set -m

pip install -e src
pytest tests -s
