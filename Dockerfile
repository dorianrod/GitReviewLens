FROM python:3.10

WORKDIR /
ENV PYTHONPATH=/

COPY . .
RUN pip install -r ./requirements.txt

RUN chmod +x /Dockerfile.sh
CMD ["/Dockerfile.sh"]


CMD if [ "$DEBUG" = "1" ]; then \
        python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m server run --host=0.0.0.0; \
    else \
        python /src/server.py; \
    fi