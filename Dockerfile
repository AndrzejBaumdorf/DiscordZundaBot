FROM python:3
USER root

RUN apt-get update && \
    apt-get -y install locales vim less ffmpeg && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 && \
    pip install --upgrade pip setuptools && \
    pip install numpy discord.py python-dotenv requests && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=JST-9
ENV TERM=xterm
