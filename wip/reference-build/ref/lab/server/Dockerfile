FROM python:3.11-slim-bookworm
RUN pip install --no-cache-dir pyftpdlib==2.2.0 cryptography==50.0.2
COPY . /srv
WORKDIR /srv
RUN python make_certs.py
CMD ["python", "/srv/services.py"]
