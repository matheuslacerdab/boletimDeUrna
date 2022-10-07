FROM python:3.8.8

WORKDIR /usr/src/app

COPY . .

RUN python -m pip install --upgrade setuptools pip wheel

RUN pip install -r requirements.txt

CMD streamlit run --server.port $PORT app.py