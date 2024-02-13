FROM python:3.10
ENV PYTHONBUFFERED 1
#ENV http_proxy http://127.0.0.1:8080
#ENV https_proxy https://127.0.0.1:8080

RUN mkdir /code

COPY ./ /code
COPY ./database_folder/db_docker.sqlite3 /code_volume/db_docker.sqlite3
WORKDIR /code
MAINTAINER Janardhan Vignarajan

# ADD requirements.txt /code/
RUN python -m venv venv
RUN python -m venv venv_yolov7
RUN python -m venv venv_df_osteo

SHELL ["/bin/bash", "-c"]

RUN source /code/venv/bin/activate && pip install -r requirements.txt && deactivate
RUN source /code/venv_yolov7/bin/activate && pip install -r /code/Yolov7_deployment/yolov7/requirements.txt && deactivate
RUN source /code/venv_df_osteo/bin/activate && pip install -r /code/df_osteo_detection_program/requirements.txt && deactivate




