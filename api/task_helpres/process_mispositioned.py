from tasks.cron.process_mispositioned_games import reprocess_mispositioned_league_games_cron

def process_mispositioned_games():
    reprocess_mispositioned_league_games_cron.apply_async()
