FROM python:3.6.9-buster

WORKDIR /project

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# For dev only
ENTRYPOINT ["tail", "-f", "/dev/null"]
#CMD [ "python", "carla.py", "--live" ]
# CMD [ "python", "./your-daemon-or-script.py" ]