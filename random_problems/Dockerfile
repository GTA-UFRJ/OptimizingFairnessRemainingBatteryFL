FROM python:3.10-slim

WORKDIR /app

COPY wf_solver/ ./wf_solver/
COPY random_problems.py .

RUN pip install --no-cache-dir ./wf_solver/. scipy 