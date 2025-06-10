import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_ADDRESS = os.getenv('REDIS_ADDRESS', default="127.0.0.1")

r = redis.Redis(
    host=REDIS_ADDRESS,
    port=6379,
    password=REDIS_PASSWORD,
    db=0,
)

def get_redis_single() -> redis.Redis:
    return r
