import re

from models import PerformanceWindowData, PerformanceTotalData


TOTAL_FIELDS = PerformanceTotalData.schema()['properties'].keys()
WINDOW_FIELDS = PerformanceWindowData.schema()['properties'].keys()

TO_EXCLUDE_FOR_LANE = []
TO_EXCLUDE_FOR_GAME = []

LANE_FIELDS = []
GAME_FIELDS = []

for _name in WINDOW_FIELDS:
    if _name.startswith('l') and not _name.endswith('_id'):
        LANE_FIELDS.append(_name)
    else:
        TO_EXCLUDE_FOR_LANE.append(_name)

    if _name.startswith('g') and not _name.endswith('_id'):
        GAME_FIELDS.append(_name)
    else:
        TO_EXCLUDE_FOR_GAME.append(_name)

id_search = re.compile(r'.*_?id$')

TOTAL_FIELDS_FILTERED = [x for x in TOTAL_FIELDS if not id_search.match(x)]
WINDOW_FIELDS_FILTERED = [x for x in WINDOW_FIELDS if not id_search.match(x)]
