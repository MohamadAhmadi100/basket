FROM python:3.9

WORKDIR /basket

COPY ./README.md /basket/README.md

COPY ./requirements.txt /basket/requirements.txt

COPY ./.env /basket/.env

COPY ./config.py /basket/config.py

COPY ./setup.py /basket/setup.py

COPY ./source /basket/source

RUN pip install -e /basket/.

CMD ["python", "/basket/source/main.py"]
