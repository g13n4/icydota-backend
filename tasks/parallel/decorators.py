import pickle
from functools import wraps
from typing import Literal

from sqlmodel import Session

from db import get_sync_db_session
from modules.key_creators.redis_key_creator import RedisParallelKeyCreator
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator, \
    team_ccomparison_query_creator
from modules.query_creators.match_aggregation_query_creator_function import match_aggregation_query_creator
from modules.query_creators.team_aggregation_query_creator_function import team_aggregation_query_creator
from redis_app import get_redis_single
from tasks.cross_comparison.helpers import COMPARISON_TYPE_POSITION_MAP


def performance_creator_task_decorator(func):
    r = get_redis_single()


    @wraps(func)
    def wrapper(*args, **kwargs):
        performance_objects, CK, key = func(*args, **kwargs)
        data = {
            "performance": { k: v.id for k, v in performance_objects.items() },
            "CK": CK,
        }
        r.set(key, pickle.dumps(data))


    return wrapper


def parallel_processing_task_decorator(func):
    r = get_redis_single()

    query_func_dict = {
        ("aggregation", "player"): match_aggregation_query_creator,
        ("aggregation", "team"): team_aggregation_query_creator,
        ("cross-comparison", "player"): match_ccomparison_query_creator,
        ("cross-comparison", "team"): team_ccomparison_query_creator,
    }


    @wraps(func)
    def wrapper(*args, **kwargs):
        processing_type: Literal["aggregation", "cross-comparison"] = kwargs.pop("processing_type")
        PoT: Literal["player", "team"] = kwargs.pop("PoT")

        db_session: Session = get_sync_db_session(expire=True)

        league_id = kwargs.pop("league_id", None)
        patch_id = kwargs.pop("patch_id", None)

        # only for aggregation player
        aggregation_type = kwargs.pop("aggregation_type", None)
        # only for cross-comparison player
        ccomparison_type = kwargs.pop("ccomparison_type", None)
        ccomp_pos_id = kwargs.pop("ccomp_pos_id", None)
        enemies = COMPARISON_TYPE_POSITION_MAP.get(ccomp_pos_id, None)

        KEY = RedisParallelKeyCreator(
            processing_type=processing_type,
            PoT=PoT,
            aggregation_type=aggregation_type or ccomparison_type or None,
            league_id=league_id,
            patch_id=patch_id,
            **kwargs
        )
        output_pickled = r.get(KEY.base)

        output = pickle.loads(output_pickled)

        result = func(
            db_session=db_session,
            league_id=league_id,
            patch_id=patch_id,
            CK=output["CK"],
            performance_map=output["performance"],
            query_func=query_func_dict[(processing_type, PoT)],
            enemies=enemies,
            ccomparison_type=ccomparison_type,
            **kwargs
        )
        return result


    return wrapper
