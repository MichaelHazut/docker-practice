FROM python:3

WORKDIR /app

COPY . /app

RUN pip install Flask mysql-connector-python

EXPOSE 80

CMD ["python", "app.py"]