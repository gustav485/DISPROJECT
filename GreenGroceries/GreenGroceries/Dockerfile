FROM python:3.9-alpine
WORKDIR /code
run mkdir GreenGroceries
RUN apk add --no-cache gcc musl-dev linux-headers postgresql postgresql-contrib libpq-dev bash musl-dev gcc libffi-dev g++
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["./GreenGroceries/entrypoint.sh"]
