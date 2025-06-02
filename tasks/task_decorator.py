from functools import wraps

from sqlmodel import Session

from db import get_sync_db_session
from models import League, Patch


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

        league_id = kwargs.get("league_id", None)
        patch_id = kwargs.get("patch_id", None)

        if league_id:
            league_obj = db_session.get(League, league_id)
            if not league_obj:
                raise ValueError("No such league in the database")

        elif patch_id:
            patch_obj = db_session.get(Patch, patch_id)
            if not patch_obj:
                raise ValueError("No such patch in the database")
        else:
            raise ValueError("No league or patch id were provided")

        result = func(db_session=db_session, **kwargs)
        return result

    return wrapper
