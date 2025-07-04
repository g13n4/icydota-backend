import os

from dotenv import load_dotenv

from redis_app import get_redis_single


load_dotenv()

REDIS_ADDRESS = os.getenv('REDIS_ADDRESS')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')


def test_redis():
    print(f"Testing redis connection...")
    print(f"Settings set: {REDIS_ADDRESS}:{6379} (password: {REDIS_PASSWORD})")
    r = get_redis_single()

    key = "hello"
    value = "world"

    r.set(key, value, ex=60)

    output = r.get(key)
    assert output == value
    r.delete(key)


if __name__ == "__main__":
    test_redis()
