import os
import time
import random

from dotenv import load_dotenv


# PREFIX
load_dotenv()

API_PREFIX = os.getenv('API_PREFIX', default='')
if API_PREFIX:
    API_PREFIX = '/' + API_PREFIX

# REQUEST DATA
HEADERS = { 'content-type': 'application/json' }
ADDRESS = "http://127.0.0.1:3333"


# FUNC
def test_output(output_data):
    for name in ["table_data", "value_mapping"]:
        if not (name in output_data):
            return False
    return True


def delay():
    time.sleep(random.uniform(0.1, 0.7))
