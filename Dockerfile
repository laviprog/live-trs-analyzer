FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

RUN apt update && apt install -y python3 python3-pip ffmpeg

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]