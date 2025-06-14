import os
from itertools import cycle

from dotenv import load_dotenv


load_dotenv()

PARSER_PORTS = os.getenv('PARSER_PORTS', "5600")
PARSER_PORTS = PARSER_PORTS.split(",")

AVAILABLE_PARSERS_PORT = cycle(PARSER_PORTS)
