import time

from utils.booking import Booking

start_time = time.time()

with Booking() as bot:
    bot.land_first_page()

    bot.remove_popups()

    bot.change_currency(
        ["U.S. Dollar", "United States Dollar", "USD", "US Dollar", "Dollar"]
    )

    bot.remove_popups()

    bot.select_place_to_go("New York")

    bot.remove_popups()

    bot.select_dates(check_in_date="2025-04-11", check_out_date="2025-04-12")

    bot.select_occupancy(
        occupancy_options=[["group_adults", 5], ["group_children", 0], ["no_rooms", 2]]
    )

    bot.click_search()

    bot.apply_filtrations()

    total_properties = bot.get_search_result_count()
    total_properties = int(total_properties.split(": ")[1].split(" ")[0])
    print(total_properties)

    bot.refresh()

    bot.report_results(total_properties)

print(f"Step execution time: {time.time() - start_time:.2f} seconds")
