from sqlmodel import select

from app.models import WindowComparisonType, WindowInfoType, WindowInfo
from ...replay_parsing.postprocessor import ALL_DATA_TO_COMPARE
from ...replay_parsing.windows import ALL_WINDOWS


async def create_window_types(db_session, ) -> None:
    sel_result = await db_session.execute(select(WindowInfo))
    db_win_info = sel_result.scalars().all()
    if db_win_info:
        return

    for wtype in ALL_WINDOWS.keys():
        wtype_obj = WindowInfoType(
            name=wtype
        )
        db_session.add(wtype_obj)
    await db_session.commit()

    sel_result = await db_session.execute(select(WindowInfoType))
    db_wtypes = sel_result.scalars().all()
    wtype_dict = {x.name: x for x in db_wtypes}

    sel_result = await db_session.execute(select(WindowComparisonType))
    db_positions = sel_result.scalars().all()
    positions_dict = {
        'carry': [x for x in db_positions if x.comparandum in [1, 2, 3]],
        'support': [x for x in db_positions if x.comparandum in [4, 5]],

        'carry_columns': [x.split('|')[1] for x in ALL_DATA_TO_COMPARE['carry']],
        'support_columns': [x.split('|')[1] for x in ALL_DATA_TO_COMPARE['support']],
    }

    for wtype, windows in ALL_WINDOWS.items():
        wtype_obj = wtype_dict[wtype]
        for window_name, column in windows.items():
            windowinfo_obj = WindowInfo(
                info_type=wtype_obj.id,
                name=window_name,
            )
            db_session.add(windowinfo_obj)

            if column in positions_dict['carry_columns']:
                for pos_obj in positions_dict['carry']:
                    windowinfo_obj = WindowInfo(
                        info_type=wtype_obj.id,
                        name=window_name,
                        comparison=pos_obj,
                    )
                    db_session.add(windowinfo_obj)

            if column in positions_dict['support_columns']:
                for pos_obj in positions_dict['support']:
                    windowinfo_obj = WindowInfo(
                        info_type=wtype_obj.id,
                        name=window_name,
                        comparison=pos_obj,
                    )
                    db_session.add(windowinfo_obj)

    await db_session.commit()
