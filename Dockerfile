FROM python:3.10
ENV PYTHONBUFFERED 1
#ENV http_proxy http://127.0.0.1:8080
#ENV https_proxy https://127.0.0.1:8080

RUN mkdir /code


WORKDIR /code
MAINTAINER Janardhan Vignarajan
SHELL ["/bin/bash", "-c"]

# ADD requirements.txt /code/
COPY requirements.txt /code/requirements_django.txt
RUN python -m venv venv
RUN source /code/venv/bin/activate && pip install -r requirements_django.txt && deactivate

COPY Yolov7_deployment/yolov7/requirements.txt /code/requirements_yolov7.txt
RUN python -m venv venv_yolov7
RUN source /code/venv_yolov7/bin/activate && pip install -r requirements_yolov7.txt && deactivate

COPY df_osteo_detection_program/requirements.txt /code/requirements_df_osteo.txt
RUN python -m venv venv_df_osteo
RUN source /code/venv_df_osteo/bin/activate && pip install -r requirements_df_osteo.txt && deactivate


COPY ./ /code
# COPY ./database_folder/db_jv.sqlite3 /code_volume/db_docker.sqlite3

