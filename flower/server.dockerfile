FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY fed_server.py .
COPY task.py . 
COPY wf_solver wf_solver/ 

RUN pip install --no-cache-dir ./wf_solver/.

RUN pip install --no-cache-dir flwr==1.11.1 && \
    pip install --no-cache-dir --default-timeout=1000 \
    torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu