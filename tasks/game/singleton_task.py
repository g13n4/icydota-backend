from celery import shared_task

from redis_app import get_redis_single


MATCH_LOCK_DURATION = 60 * 60 * 2


def is_match_locked(match_id: int) -> bool:
    r = get_redis_single()

    match_key = f"match-{match_id}"
    output = r.get(match_key)

    # No lock exists so we create one
    if output is None:
        r.set(match_key, "", MATCH_LOCK_DURATION)
        return False

    return True


@shared_task(name='fake_match_task', ignore_result=True)
def fake_match_task(*args, **kwargs):
    return None
