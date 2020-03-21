FROM alpine
WORKDIR /app
COPY . /app
ENV TEAM_ID CC_455_444_446_447
RUN apk add --no-cache python-dev
RUN apk add --no-cache py-pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 80
CMD ["python", "am.py"]