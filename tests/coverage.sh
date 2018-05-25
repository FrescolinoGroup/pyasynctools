#!/bin/bash
py.test -p no:cov-exclude --cov=fsc.async_tools --cov-report=html
