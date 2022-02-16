# Author: Janardhan Vignarajan
# Description: This is the config file for gunicorn in production environment.
import multiprocessing

bind = "0.0.0.0:8000"
loglevel = "debug"
workers = multiprocessing.cpu_count() * 2 + 1
reload = True
timeout = 300

errorlog = "./gunicorn_error.log"
accesslog = "./gunicorn_access.log"
