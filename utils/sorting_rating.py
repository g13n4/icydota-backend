import re


def performance_data_sort_rating(name: str) -> int:
    # WINDOWS
    if (re_match := re.match(r'^([lg])(\d+|total)(plus)?', name)):
        code, value, *plus = re_match.groups()

        return ((1000 if code == 'g' else 0) +
                (int(value) if value != 'total' else 100) +
                (0 if plus[0] is None else 1))
    else:
        # TOTALS
        if 'gold' in name:
            return 0
        if 'xp' in name:
            return 1
        if 'hero_kills' in name:
            return 2
        if 'kda' in name:
            return 3
        if 'kills_per_minute' in name:
            return 4
        if 'lane_kills' in name:
            return 5
        if 'neutral_kills' in name:
            return 6
        if 'ancient_kills' in name:
            return 7
        if 'tower_kills' in name:
            return 8
        if 'roshan_kills' in name:
            return 9
        if 'courier_kills' in name:
            return 10
        if 'observer_uses' in name:
            return 11
        if 'sentry_uses' in name:
            return 12
        if 'runes_picked_up' in name:
            return 13
        if 'buyback_count' in name:
            return 14

        score = 0
        if 'lane_efficiency' in name:
            score += 100
        if re.match(r'first_(blood|kill)', name):
            score += 200
        if re.match('(died_first)|(first_death)', name):
            score += 300
        if 'lost_tower' in name:
            score += 400
        if 'destroyed_tower' in name:
            score += 500
        if 'lane' in name:
            score += 15
        if 'time' in name:
            score += 10

        return score


def gamedata_sort_rating(name: str) -> int:
    score = 0

    if 'gold' in name:
        score += 100
    if 'xp' in name:
        score += 90
    if 'hero' in name:
        score += 80
    if 'first_blood_claimed' in name:
        score += 85
    if 'kpm' in name:
        score += 70
    if 'runes_picked_up' in name:
        score += 60

    if re.match(r'.*_|kills', name):
        score += 50
    if re.match('.*_|placed', name):
        score += 45
    if 'roshan' in name:
        score += 4
    if 'obs_' in name:
        score += 3
    if 'sentry_' in name:
        score += 2

    if 'destroyed_tower' in name:
        score += 500
    if 'lane' in name:
        score += 15
    if 'first_blood_claimed' in name:
        score += 10

    return score
