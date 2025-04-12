"""
This file will include a class that will be responsible to apply filtrations.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BookingFiltration:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def apply_star_rating(self, star_values):
        wait = WebDriverWait(self.driver, 10)

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-testid="filters-group-container"]')
                )
            )

            for star in star_values:
                try:
                    # Find the checkbox using the data attribute pattern
                    checkbox_selector = f"input[name='class={star}']"
                    checkbox = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, checkbox_selector)
                        )
                    )

                    # Scroll the element into view before clicking
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", checkbox
                    )
                    time.sleep(0.5)

                    # Click using JavaScript
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    print(f"✅ CLICKED checkbox for {star} star(s)")
                    time.sleep(0.5)

                except Exception as e:
                    print(f"[Error selecting {star} star rating] {str(e)}")

        except Exception as e:
            print(f"[Star Rating Filter Error] {str(e)}")

    def select_sort_option(self, sort_option):
        """
        Select a sorting option from the dropdown.

        Args:
            sort_option (str): One of "Price (lowest first)", "Price (highest first)",
                            "Top reviewed", "Our top picks", "Homes & apartments first"
        """
        wait = WebDriverWait(self.driver, 10)

        # Dictionary mapping user-friendly names to data-id attributes
        sort_option_mapping = {
            "Price (lowest first)": "price",
            "Price (highest first)": "price_from_high_to_low",
            "Top reviewed": "bayesian_review_score",
            "Our top picks": "popularity",
            "Homes & apartments first": "upsort_bh",
        }

        if sort_option not in sort_option_mapping:
            print(f"⚠️ Invalid sort option: {sort_option}")
            print(f"Valid options are: {', '.join(sort_option_mapping.keys())}")
            return

        data_id = sort_option_mapping[sort_option]

        try:
            # Find and click the sort dropdown button to open it
            sort_dropdown_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-testid="sorters-dropdown-trigger"]')
                )
            )

            # Scroll the dropdown trigger button into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", sort_dropdown_button
            )
            time.sleep(0.5)

            # Click to open the dropdown
            sort_dropdown_button.click()
            print("✅ Clicked sort dropdown button")
            time.sleep(1)  # Wait for dropdown to appear

            # Find and click the specific sort option by data-id
            sort_option_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'button[data-id="{data_id}"]')
                )
            )

            # Scroll to the option if needed (some options might be out of view in the dropdown)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", sort_option_button
            )
            time.sleep(0.5)

            # Click the sort option
            sort_option_button.click()
            print(f"✅ Selected sort option: {sort_option}")
            time.sleep(1)  # Wait for the page to update

        except Exception as e:
            print(f"[Sort Option Selection Error] {str(e)}")
