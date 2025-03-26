FROM python:3.10-slim

RUN apt update && apt install ffmpeg -y

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]