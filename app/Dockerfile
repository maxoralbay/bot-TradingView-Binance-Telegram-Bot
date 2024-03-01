FROM python:3.10
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV FLASK_APP=app.py
EXPOSE 5000

