FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1
WORKDIR /
COPY requirements.txt /
RUN python3 -m venv local-env
RUN source local-env/bin/activate
RUN pip install -r requirements.txt
COPY source /source
COPY main.py /.

CMD [ "python", "main.py" ]