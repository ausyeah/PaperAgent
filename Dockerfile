FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "paperagent.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
