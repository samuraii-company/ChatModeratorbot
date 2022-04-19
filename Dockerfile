FROM python:3.10
RUN mkdir -p /bot/

WORKDIR /bot/
COPY . /bot/

RUN pip3 install -r req.txt
CMD ["python3", "main.py"]