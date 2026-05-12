FROM python:3.14.4-alpine
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers postgresql postgresql-contrib libpq-dev bash musl-dev gcc libffi-dev g++
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .

ENTRYPOINT ["./entrypoint.sh"]
