import datetime
from pydantic import BaseModel
from uuid import uuid4
from kazoo.client import KazooClient

from fastapi import FastAPI

from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.server_id = uuid4()
    app.url_shortener = URLShortener(app.server_id)
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)

async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient("mongodb://root:root@localhost:27017/")
    await app.mongodb_client.admin.command('ping')
    app.mongodb = app.mongodb_client.get_database("url_shortener")
    print("MongoDB connected.")

async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"health": "is wealth", "id": app.server_id}

#########

class URLMapping(BaseModel):
    long_url: str
    short_url: str
    created_at: datetime.datetime

#########
 
ZK_HOSTS = 'localhost:2181'
RANGE_SIZE = 1000

class URLShortener:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.zk = KazooClient(hosts=ZK_HOSTS)
        self.zk.start()
        
        self.range_start = -1
        self.range_end = -1
        self.zk_path = "/url-shortener/next_global_range_start"
        
        if not self.zk.exists(self.zk_path):
            self.zk.create(self.zk_path, b"0", makepath=True) # set initial value to 0
    
    def get_next_counter(self):
        self.range_start += 1
        if self.range_start < self.range_end:
            return self.range_start
        else:
            data, stat = self.zk.get(self.zk_path)
            print(data, stat)
            self.range_start = int(data.decode())
            self.range_end = self.range_start + RANGE_SIZE - 1
            self.zk.set(self.zk_path, str(self.range_end + 1).encode(), version=stat.version) # TODO handle version mismatch (BadVersionError) -> https://kazoo.readthedocs.io/en/latest/api/client.html#kazoo.client.KazooClient.set
            return self.range_start
    
    def base62_encode(self, num):
        base62_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return "0"
        result = ""
        while num > 0:
            result = base62_chars[num % 62] + result
            num //= 62
        return result
            
    def get_shorten_url(self):
        counter = self.get_next_counter()
        print(counter)
        short_url = self.base62_encode(counter)
        return short_url

#########

@app.post("/shorten")
async def shorten(url: str):
    short_url = app.url_shortener.get_shorten_url()
    url_mapping = URLMapping(long_url=url, short_url=f"{short_url}", created_at=datetime.datetime.utcnow())
    result = await app.mongodb["mapping"].insert_one(url_mapping.dict())
    return url_mapping.dict()

@app.get("/resolve/{url}", response_model=URLMapping)
async def resolve_url(url: str):
    result = await app.mongodb["mapping"].find_one({"short_url": f"{url}"})
    return result
