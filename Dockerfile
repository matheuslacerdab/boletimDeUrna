FROM python:3.8

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

CMD streamlit run --server.port $PORT app.py