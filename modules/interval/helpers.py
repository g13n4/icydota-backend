def get_line_data(line: dict, *fields):
    time = line["time"]
    slot = line["slot"]

    if fields:
        return time, slot, *(line[x] for x in fields)
    else:
        return time, slot
