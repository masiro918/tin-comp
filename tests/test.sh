#!/bin/sh

coverage run -m pytest -vv end2end_test.py && coverage html
