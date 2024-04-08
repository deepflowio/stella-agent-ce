#!/bin/bash

set -e

echo "Starting py2c.sh script"

cp llm_agent_app/llm_agent.py llm_agent_app/llm_agent.pyx

/root/venv/bin/python3 setup.py build_ext  -i

rm llm_agent_app/llm_agent.py
rm llm_agent_app/llm_agent.c

echo "py2c.sh script finished"