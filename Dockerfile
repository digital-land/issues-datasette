FROM python:3.10
COPY . /app
WORKDIR /app

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT
CMD datasette serve -h 0.0.0.0 -p $PORT  --inspect-file data/dataset-issue.json --immutable data/dataset-issue.sqlite3
