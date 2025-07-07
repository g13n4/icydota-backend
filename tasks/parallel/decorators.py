import pickle
from functools import wraps

from sqlmodel import Session

from db import get_sync_db_session
from redis_app import get_redis_single
from tasks.cross_comparison.helpers import COMPARISON_TYPE_POSITION_MAP
from tasks.parallel.parallel_helpers import get_parallel_processing_helpers


def performance_creator_task_decorator(func):
    r = get_redis_single()


    @wraps(func)
    def wrapper(*args, **kwargs):
        db_session: Session = kwargs["db_session"]

        performance_objects, rkey = func(*args, **kwargs)

        db_session.commit()
        db_session.flush(performance_objects.values())

        data = { }
        for k, obj in performance_objects.items():
            if obj.id is None:
                raise KeyError("No performance objects to set!")
            else:
                data[k] = obj.id

        r.set(rkey, pickle.dumps(data), ex=60 * 60 * 24)


    return wrapper


def parallel_processing_task_decorator(func):
    r = get_redis_single()


    @wraps(func)
    def wrapper(*args, **kwargs):
        db_session: Session = get_sync_db_session(expire=True)

        ccomp_pos_id = kwargs.pop("ccomp_pos_id", None)
        enemies = COMPARISON_TYPE_POSITION_MAP.get(ccomp_pos_id, None)

        KC, KEY, query = get_parallel_processing_helpers(with_query=True, ccomp_pos_id=ccomp_pos_id, **kwargs)

        output_pickled = r.get(KEY)
        output = pickle.loads(output_pickled)

        result = func(
            db_session=db_session,
            KC=KC,
            performance_map=output,
            query_func=query,
            positions=enemies,
            **kwargs
        )
        return result


    return wrapper
