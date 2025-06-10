import pickle
from functools import wraps
from typing import Literal

from sqlmodel import Session

from db import get_sync_db_session
from models import League, Patch
from redis_app import get_redis_single
from tasks.aggregation.player.parallel.helpers import PlayerParallelKeyCreator


def processing_task_decorator(func):
    """
    Decorates functions that require both league_id and patch_id.
    Checks if they exist in the db.
    :param func:
    :return: Callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        db_session: Session = get_sync_db_session(expire=False)

        league_id = kwargs.pop("league_id", None)
        patch_id = kwargs.pop("patch_id", None)

        if league_id:
            league_obj = db_session.get(League, league_id)
            if not league_obj:
                raise ValueError("No such league in the database")

        elif patch_id:
            patch_obj = db_session.get(Patch, patch_id)
            if not (patch_obj and patch_obj.aggregation_allowed):
                raise ValueError("No such patch in the database")
        else:
            raise ValueError("No league or patch id were provided")

        result = func(db_session=db_session, league_id=league_id, patch_id=patch_id, **kwargs)
        return result

    return wrapper


def parallel_processing_task_decorator(
        processing_type: Literal["aggregation", "cross-comparison"],
        PoT: Literal["player", "team"],
):
    def parallel_processing_task_decorator_inner(func):
        r = get_redis_single()

        @wraps(func)
        def wrapper(*args, **kwargs):
            db_session: Session = get_sync_db_session(expire=True)

            league_id = kwargs.pop("league_id", None)
            patch_id = kwargs.pop("patch_id", None)
            aggregation_type = kwargs.pop("aggregation_type")

            KEY = PlayerParallelKeyCreator(
                processing_type=processing_type,
                PoT=PoT,
                aggregation_type=aggregation_type,
                league_id=league_id,
                patch_id=patch_id,
            )
            output_pickled = r.get(KEY.base)

            output = pickle.loads(output_pickled)

            result = func(
                db_session=db_session,
                league_id=league_id,
                patch_id=patch_id,
                AGC=output["AGC"],
                performance_map=output["performance"],
                **kwargs)
            return result

        return wrapper
    return parallel_processing_task_decorator_inner
