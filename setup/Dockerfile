FROM python:3.7.10-slim

RUN mkdir /project

WORKDIR /project
COPY . .

RUN cd setup && chmod u+x setup.sh && ./setup.sh local

ENTRYPOINT [ "python3" ]
