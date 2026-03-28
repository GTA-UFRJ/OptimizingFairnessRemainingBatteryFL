FROM python:3.10-slim

WORKDIR /app

COPY fed_client.py .
COPY task.py . 

RUN pip install flwr==1.11.1
RUN pip install json
RUN pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
