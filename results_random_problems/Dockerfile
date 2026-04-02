FROM python:3.10-slim

WORKDIR /app

RUN pip install matplotlib numpy pandas

COPY scripts/plot_*.py ./
COPY guiaraujo.mplstyle ./
COPY scripts/plot_all.sh ./

RUN chmod +x plot_all.sh

CMD ["./plot_all.sh"]