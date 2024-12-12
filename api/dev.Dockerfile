FROM python:3.11

WORKDIR /app

COPY . .
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev
RUN pip install -U pip
RUN pip install -r dev.requirements.txt

CMD python main.py
