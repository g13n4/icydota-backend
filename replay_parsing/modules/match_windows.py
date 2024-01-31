early_game_windows = [(-90, 60 * 2, 'l2'),  # first 2 minutes
                      (60 * 2, 60 * 4, 'l4'),  # 2-4
                      (60 * 4, 60 * 6, 'l6'),  # 4-6
                      (60 * 6, 60 * 8, 'l8'),  # 6-8
                      (60 * 8, 60 * 10, 'l10'), ]  # 8-10

late_game_windows = [(-90, 60 * 15, 'g15'),  # first 15 minutes
                     (60 * 15, 60 * 30, 'g30'),  # 15 - 30
                     (60 * 30, 60 * 45, 'g45'),  # 30 - 45
                     (60 * 45, 60 * 60, 'g60'),  # 45 - 60
                     (60 * 60, 60 * 60 * 60, 'g60plus'), ]  # 60 - inf

GAME_WINDOWS = early_game_windows + late_game_windows
