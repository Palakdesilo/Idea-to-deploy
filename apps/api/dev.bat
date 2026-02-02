@echo off
python -m hypercorn main:app --bind 0.0.0.0:4000 --reload