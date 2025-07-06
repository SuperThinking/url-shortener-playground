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

--------------


Working theory in brief
```
- Keeping the length of the shorten url to 7 digits as of now, with characters in range [0-9a-zA-Z] (total 62 characters). Which means total combinations possible 62^7 = 3.5 trillion combinations.
- When the user calls `shorten` endpoint with there "url", we use a distributed counter and base62 encode it to generate a unique short url.
- To maintain this distributed counter range - we use zookeeper.
- Whenever a new service is added to the system or the counter range is exhausted, we use zookeeper to increment and get the next counter.
```
