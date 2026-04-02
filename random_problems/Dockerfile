FROM python:3.10-slim

WORKDIR /app

COPY wf_solver/ ./wf_solver/
COPY random_problems.py .

RUN pip install ./wf_solver/. scipy 