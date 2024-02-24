from sqlmodel import Session
from sqlmodel import select

from models import PerformanceDataCategory, PerformanceDataType
from replay_parsing.windows import ALL_WINDOWS


def create_performance_data_tags(db_session: Session, ) -> None:
    test_obj = db_session.exec(select(PerformanceDataCategory))
    PDC_ojbs = test_obj.all()
    if PDC_ojbs:
        return

    for wtype, wdict in ALL_WINDOWS.items():

        pdt_objs = []
        for pdt_name in wdict.keys():
            pdt_obj = PerformanceDataType(
                name=pdt_name,
            )
            pdt_objs.append(pdt_obj)
            db_session.add(pdt_obj)

        wtype_obj = PerformanceDataCategory(
            name=wtype,
            data_type=pdt_objs,
        )

        db_session.add(wtype_obj)
    db_session.commit()


def delete_performance_data_tags(db_session: Session, ) -> None:
    test_obj = db_session.exec(select(PerformanceDataCategory))
    PDC_ojbs = test_obj.all()
    for PDC_obj in PDC_ojbs:
        db_session.delete(PDC_obj)
    db_session.commit()
