FROM python:3.6-slim
RUN apt-get update && apt-get upgrade -y && apt-get install -y libxml2-dev libxslt-dev sqlite3 git curl
WORKDIR /app/

# copy in required files
COPY ./*.py /app/
COPY ./setup.sh /app/
COPY ./requirements.txt /app/
# add the ctf folder
ADD ctf /app/ctf
# install requirements
RUN pip3 install cython
RUN pip3 install -r /app/requirements.txt

# CMD cd /app/ &&  python run.py
#CMD ["gunicorn", "ctf.ctf_factory:app", "-b 127.0.0.1:5051"]
