FROM docker.io/python:3.11.11-slim-bookworm

WORKDIR /app

COPY . .

RUN chmod +x make_logs.sh

RUN chmod +x follow_logs.sh

RUN chmod +x cease_logs.sh

RUN chmod +x replace_logs.sh

CMD ["/bin/bash", "-c", "./make_logs.sh && ./follow_logs.sh"]
