import os

from celery import shared_task
from dotenv import load_dotenv

from redis_app import get_redis_single


load_dotenv()

try:
    MATCH_LOCK_DURATION = int(os.getenv('MATCH_LOCK_DURATION', default=60 * 60 * 2))
except ValueError:
    MATCH_LOCK_DURATION = 60 * 60 * 2


def is_match_locked(match_id: int) -> bool:
    if MATCH_LOCK_DURATION:
        r = get_redis_single()

        match_key = f"match-{match_id}"
        output = r.get(match_key)

        # No lock exists so we create one
        if output is None:
            r.set(match_key, "", MATCH_LOCK_DURATION)
            return False

        return True
    else:
        return False


@shared_task(name='fake_match_task', ignore_result=True)
def fake_match_task(*args, **kwargs):
    return None
