FROM python:3.11.7

WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app
COPY requirements_docker.txt . 
RUN pip install --no-cache-dir -r /usr/src/app/requirements_docker.txt
RUN pip install solcore --config-setting=setup-args="-Dwith_pdd=false"
RUN pip install rayflare==1.2.1
WORKDIR /usr/src/app
COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]