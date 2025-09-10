import os
from pathlib import Path


MAIN_FOLDER_PATH = Path(__file__).parent.absolute()
BASE_REPLAY_PATH = os.path.join(MAIN_FOLDER_PATH, Path('./replays'))
assert Path(BASE_REPLAY_PATH).is_dir() == True
