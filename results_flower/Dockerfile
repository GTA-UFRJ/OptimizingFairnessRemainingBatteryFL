FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir matplotlib numpy pandas

COPY scripts/*.py ./
COPY guiaraujo.mplstyle ./
COPY scripts/pipeline.sh ./

RUN chmod +x pipeline.sh

CMD ["./pipeline.sh"]
