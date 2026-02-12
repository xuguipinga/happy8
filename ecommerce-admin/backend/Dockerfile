FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
