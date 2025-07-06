# URL SHORTENER PLAYGROUND


To run the application locally:
```bash
make venv
make install-dev
make docker-dev
source .venv/bin/activate
fastapi dev main.py
```

```
Create / View records in database (mongodb):

http://localhost:8084/

username: admin
password: pass
```

```
Shorten a URL:

curl -X 'POST' \
  'http://127.0.0.1:8000/shorten?url=haha.com' \
  -H 'accept: application/json' \
  -d ''
```

```
Resolve a shorten URL:

curl -X 'GET' \
  'http://127.0.0.1:8000/resolve/1Ie' \
  -H 'accept: application/json'
```
