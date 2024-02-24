# from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Session, select, and_


def get_items(db: Session, model, offset: int = 0, limit: int = 100):
    return db.exec(select(model).offset(offset).limit(limit)).all()


def get_performance_windows_items(db: Session, model, league_id: int, data_type_id: int, offset: int = 0, limit: int = 120):
    return (db.exec(select(model)
                    .where(and_(model.league_id == league_id, model.data_type_id == data_type_id))
                    .offset(offset)
                    .limit(limit))
            .all())


def get_performance_total_items(db: Session, model, league_id: int, offset: int = 0, limit: int = 120):
    return (db.exec(select(model)
                    .where(model.league_id == league_id)
                    .offset(offset)
                    .limit(limit))
            .all())
