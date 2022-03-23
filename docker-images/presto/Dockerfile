FROM python:3.9-buster

RUN pip install click
RUN pip install presto-client==0.302.0

COPY docker-images/presto/run_presto.py /app/run_presto.py

CMD ["python", "/app/run_presto.py"]
