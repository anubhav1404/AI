# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# system deps - adjust as needed
RUN apt-get update && apt-get install -y build-essential git curl gcc

# copy requirements first for caching
COPY requirement.txt .

# ensure psycopg2 builds via binary wheel (psycopg2-binary)
RUN pip install --upgrade pip
RUN pip install -r requirement.txt

# copy app
COPY . .

# Expose Streamlit port
EXPOSE 8501

# default command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
