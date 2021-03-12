FROM python:3.7.10-slim

RUN mkdir /project

WORKDIR /project
COPY . .

RUN chmod u+x setup/setup.sh && ./setup/setup.sh local

ENTRYPOINT [ "python3" ]
