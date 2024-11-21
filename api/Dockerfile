FROM python:3.11.0

WORKDIR /app

COPY api .
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev
RUN pip install -U pip
# RUN pip install -r pytorch-openpose/requirements.txt
RUN pip install -r requirements.txt

CMD python main.py