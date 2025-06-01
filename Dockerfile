FROM python

WORKDIR /medai

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "medaibackend"]
