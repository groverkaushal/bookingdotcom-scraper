import time

from utils.booking import Booking
from utils.settings import (
    BASE_URL,
    CHECK_IN_DATE_TO_SELECT,
    CHECK_OUT_DATE_TO_SELECT,
    CURRENCY_TO_SELECT,
    OCCUPANCY_OPTIONS_TO_SELECT,
    OUTPUT_DIR_PATH,
    PLACE_TO_SELECT,
    SELENIUM_DRIVERS_PATH,
    SORT_OPTION_TO_SELECT,
    STAR_RATING_TO_SELECT,
)

# MAIN LOGIC
start_time = time.time()

with Booking(driver_path=SELENIUM_DRIVERS_PATH) as bot:
    bot.land_first_page(BASE_URL)
    bot.remove_popups()
    bot.change_currency(currency_variants=CURRENCY_TO_SELECT)
    bot.remove_popups()
    bot.select_place_to_go(PLACE_TO_SELECT)
    bot.remove_popups()
    bot.select_dates(CHECK_IN_DATE_TO_SELECT, CHECK_OUT_DATE_TO_SELECT)
    bot.select_occupancy(OCCUPANCY_OPTIONS_TO_SELECT)
    bot.click_search()
    bot.apply_filtrations(STAR_RATING_TO_SELECT, SORT_OPTION_TO_SELECT)

    total_properties = bot.get_search_result_count()
    total_properties = int(total_properties.split(": ")[1].split(" ")[0])

    bot.refresh()
    bot.report_results(total_properties, OUTPUT_DIR_PATH)

print(f"Scraper finished! Execution time: {time.time() - start_time:.2f} seconds")
