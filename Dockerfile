FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONWRITEBYTECODE=1 \
    BOT_WORKDIR=/app

WORKDIR $BOT_WORKDIR

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]