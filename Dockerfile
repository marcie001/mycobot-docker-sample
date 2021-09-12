FROM python:3.9.7-bullseye
WORKDIR /work
ADD src requirements.txt ./
RUN pip install -r requirements.txt
CMD python main.py
