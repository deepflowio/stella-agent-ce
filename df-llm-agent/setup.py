from setuptools import setup
from Cython.Build import cythonize
import os

pwd = os.getcwd()
setup(ext_modules=cythonize([f"{pwd}/llm_agent_app/llm_agent.pyx"]))
