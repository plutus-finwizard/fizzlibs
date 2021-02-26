#!/bin/bash
  
# turn on bash's job control
set -m

pip install -e .
pytest tests -s
