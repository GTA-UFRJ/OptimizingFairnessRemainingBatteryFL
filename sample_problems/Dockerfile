FROM python:3.10-slim

WORKDIR /app

COPY wf_solver/ ./wf_solver/
COPY sample_problem.py .
COPY cases/ ./cases/

RUN pip install --no-cache-dir ./wf_solver/.