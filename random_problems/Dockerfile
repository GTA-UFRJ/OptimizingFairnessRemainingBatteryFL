FROM python:3.10-slim

WORKDIR /app

COPY wf_solver/ ./wf_solver/
COPY requirements.txt .
COPY random_problems.py .

RUN pip install -e ./wf_solver/. json scipy 