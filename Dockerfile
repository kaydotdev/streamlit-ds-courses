FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .streamlit/ .streamlit/
COPY data/ data/
COPY pages/ pages/
COPY static/ static/
COPY Introduction.py Introduction.py

CMD [ "streamlit", "run", "Introduction.py", "--server.port", "80" ]
