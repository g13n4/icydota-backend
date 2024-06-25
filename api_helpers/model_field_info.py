import re
import copy
from models import PerformanceWindowData, PerformanceTotalData


def sort_weights_generator(text: str) -> int:
    if (match := re.search(r'(\d+)', text)):
        weight = int(match[1])
        if text.endswith('plus'):
            return weight + 10

        return weight

    # total
    return 100


TOTAL_FIELDS = PerformanceTotalData.schema()['properties'].keys()
WINDOW_FIELDS = PerformanceWindowData.schema()['properties'].keys()

TO_EXCLUDE_FOR_LANE = []
TO_EXCLUDE_FOR_GAME = []

LANE_FIELDS = []
GAME_FIELDS = []

for _name in WINDOW_FIELDS:
    if _name.startswith('l') and not _name.endswith('_id') and not _name.endswith('_empty'):
        LANE_FIELDS.append(_name)
    else:
        TO_EXCLUDE_FOR_LANE.append(_name)

    if _name.startswith('g') and not _name.endswith('_id') and not _name.endswith('_empty'):
        GAME_FIELDS.append(_name)
    else:
        TO_EXCLUDE_FOR_GAME.append(_name)

LANE_FIELDS_W_EMPTY = copy.deepcopy(LANE_FIELDS) + ['l_empty']
GAME_FIELDS_W_EMPTY = copy.deepcopy(GAME_FIELDS) + ['g_empty']

LANE_FIELDS.sort(key=lambda x: sort_weights_generator(x))
GAME_FIELDS.sort(key=lambda x: sort_weights_generator(x))

id_search = re.compile(r'.*_?id$')

TOTAL_FIELDS_FILTERED = [x for x in TOTAL_FIELDS if not id_search.match(x)]
WINDOW_FIELDS_FILTERED = [x for x in WINDOW_FIELDS if not id_search.match(x)]
