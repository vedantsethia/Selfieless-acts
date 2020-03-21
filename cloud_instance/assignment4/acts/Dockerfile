ls
FROM scratch
ADD alpine-minirootfs-3.7.3-x86_64.tar.gz /
WORKDIR /app
COPY acts_app.py /app
RUN mkdir /data
RUN apk add --no-cache
RUN apk add --update python py-pip
RUN pip install Flask
RUN pip install -U flask-cors
RUN pip install requests
EXPOSE 80
ENV TEAM_ID CC_311_315_359_362
CMD ["python","acts_app.py"]
