#!/bin/bash
  
# turn on bash's job control
set -m

pip install -e .
# pytest tests -s

# Run flask app
flask run --host=0.0.0.0
