FROM python:3.10-slim

WORKDIR /app

COPY generate_iid_datasets.py .
COPY config.ini . 

RUN pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu

CMD ["sh", "-c", "python generate_iid_datasets.py"]