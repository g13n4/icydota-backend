import inspect


class TaskReason:
    PROCESS_ONE_MATCH = 1
    PROCESS_LEAGUE = 2
    PROCESS_LEAGUE_CRON = 3
    PROCESS_BAD_GAMES_CRON = 4
    PROCESS_MISPOSITIONED_GAMES_CRON = 5
    PROCESS_ONE_MATCH_SCRIPT = 6

    VALUES_DICT: dict[int, str]


    @staticmethod
    def to_logger_extra(value: int | None) -> dict:
        if value is None:
            return { }
        return { "reason": TaskReason.VALUES_DICT.get(value, None) }


    @staticmethod
    def to_str(value: int | None) -> str:
        if value is None or value not in TaskReason.VALUES_DICT:
            return ""
        return f"({TaskReason.VALUES_DICT[value]})"


TaskReason.VALUES_DICT = {
    v: k for k, v in inspect.getmembers(TaskReason)
    if not k.startswith("__") and not inspect.isfunction(v)
}
