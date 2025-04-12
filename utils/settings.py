import ast
import os

from dotenv import load_dotenv

load_dotenv("./.env")

BASE_URL = os.getenv("BASE_URL")
SELENIUM_DRIVERS_PATH = os.getenv("SELENIUM_DRIVERS_PATH")
OUTPUT_DIR_PATH = os.getenv("OUTPUT_DIR_PATH")

CURRENCY_TO_SELECT = os.getenv("CURRENCY_TO_SELECT")
PLACE_TO_SELECT = os.getenv("PLACE_TO_SELECT")
CHECK_IN_DATE_TO_SELECT = os.getenv("CHECK_IN_DATE_TO_SELECT")
CHECK_OUT_DATE_TO_SELECT = os.getenv("CHECK_OUT_DATE_TO_SELECT")
OCCUPANCY_OPTIONS_TO_SELECT = ast.literal_eval(os.getenv("OCCUPANCY_OPTIONS_TO_SELECT"))

STAR_RATING_TO_SELECT = ast.literal_eval(os.getenv("STAR_RATING_TO_SELECT"))
SORT_OPTION_TO_SELECT = os.getenv("SORT_OPTION_TO_SELECT")
