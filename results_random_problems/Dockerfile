FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir matplotlib numpy pandas

COPY scripts/plot_*.py ./
COPY scripts/plot_all.sh ./

RUN chmod +x plot_all.sh

CMD ["./plot_all.sh"]