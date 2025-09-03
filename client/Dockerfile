FROM python:3.9.7-slim
COPY client /
COPY common /infrastructure/common
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "main.py"]