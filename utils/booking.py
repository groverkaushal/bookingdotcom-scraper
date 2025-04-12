import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.booking_filtration import BookingFiltration


class Booking(webdriver.Chrome):
    def __init__(self, driver_path, teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ["PATH"] += self.driver_path
        super(Booking, self).__init__()
        # self.implicitly_wait(2)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def land_first_page(self, base_url):
        self.get(base_url)
        WebDriverWait(self, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page fully loaded.")

    def remove_popups(self):
        try:
            # Wait for the dialog to be present (timeout after 10s)
            dialog = WebDriverWait(self, 5).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div[role='dialog'][aria-label^='Window offering discounts']",
                    )
                )
            )

            if dialog.is_displayed():
                print("Popup Dialog is present! Removing it....")
                try:
                    dismiss_button = dialog.find_element(
                        By.CSS_SELECTOR, "button[aria-label='Dismiss sign-in info.']"
                    )
                    dismiss_button.click()
                    print("Dialog dismissed.")
                except:
                    raise Exception("Dialog could not be removed")
        except:
            print("Dialog not displayed. continuing...")

    def change_currency(self, currency_variants):
        wait = WebDriverWait(self, 5)
        # Ensure the currency picker button is visible and clickable
        currency_button = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "button[data-testid='header-currency-picker-trigger']",
                )
            )
        )
        currency_button.click()

        # Try multiple currency options
        for variant in currency_variants:
            try:
                currency_option = wait.until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            f"//button[@data-testid='selection-item' and contains(., '{variant}')]",
                        )
                    )
                )
                currency_option.click()
                break
            except TimeoutException:
                continue
        else:
            raise Exception(
                f"[Currency Change Failed] None of the currency variants matched: {currency_variants}"
            )

        print("Currency successfully changed!")

    def select_place_to_go(self, place_to_go):
        wait = WebDriverWait(self, 3)
        try:
            search_field = wait.until(EC.visibility_of_element_located((By.NAME, "ss")))
            search_field.clear()
            search_field.send_keys(place_to_go)
            time.sleep(2)
            first_result = wait.until(
                EC.element_to_be_clickable((By.ID, "autocomplete-result-0"))
            )
            first_result.click()
        except:
            raise Exception("Error in selecting place to go")

        print(f"selected place to go: {place_to_go}")

    def select_dates(self, check_in_date, check_out_date):
        # TODO: add a filter to raise if the dates are older than current date
        wait = WebDriverWait(self, 1)

        try:
            # Wait for the check-in date element to be clickable
            check_in_element = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'span[data-date="{check_in_date}"]')
                )
            )
            check_in_element.click()

            # Wait for the check-out date element to be clickable
            check_out_element = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'span[data-date="{check_out_date}"]')
                )
            )
            check_out_element.click()

            print(
                f"[Dates Selected] Check-in: {check_in_date}, Check-out: {check_out_date}"
            )

        except Exception as e:
            print(f"[Date Selection Error] {e}")

    def select_occupancy(self, occupancy_options):
        wait = WebDriverWait(self, 10)

        try:
            occupancy_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[data-testid='occupancy-config']")
                )
            )
            occupancy_button.click()
        except Exception as e:
            print(f"[Occupancy Selector Error] {e}")
            return

        try:
            for occ_id, target_val in occupancy_options:
                container = self.find_element(
                    By.XPATH, f"//input[@id='{occ_id}']/parent::div"
                )
                input_elem = container.find_element(By.ID, occ_id)
                buttons = container.find_elements(
                    By.XPATH, ".//following-sibling::div//button"
                )

                if len(buttons) < 2:
                    print(
                        f"[Occupancy Adjustment Error] Buttons not found for {occ_id}"
                    )
                    continue
                minus_btn, plus_btn = buttons[0], buttons[1]

                while True:
                    current_val = int(input_elem.get_attribute("value").strip())
                    print(f"[Current {occ_id}] {current_val}")
                    if current_val == target_val:
                        break
                    elif current_val < target_val:
                        plus_btn.click()
                    else:
                        minus_btn.click()
                    time.sleep(0.4)

        except Exception as e:
            print(f"[Adjusting Occupancy Error] {e}")

    def click_search(self):
        search_button = self.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        search_button.click()

    def apply_filtrations(self, star_values, sort_option):
        filtration = BookingFiltration(driver=self)
        filtration.apply_star_rating(star_values)

        filtration.select_sort_option(sort_option)

    def get_search_result_count(self):
        """
        Extracts the search result header text (e.g., 'New York: 447 properties found')
        from the results page.

        Returns:
            str: The text of the result header, or None if not found.
        """
        try:
            wait = WebDriverWait(self, 10)
            header_elem = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1[aria-label*='properties found']")
                )
            )
            result_text = header_elem.text
            print(f"📝 Search results header: {result_text}")
            return result_text
        except Exception as e:
            print(f"[❌ Error getting search result text] {e}")
            return None

    def report_results(self, total_properties, output_dir):

        # Function to safely extract inner text
        def safe_find_text(el, selector):
            try:
                return el.find_element(By.CSS_SELECTOR, selector).text.strip()
            except:
                return ""

        # Function to safely extract an attribute
        def safe_find_attr(el, selector, attr):
            try:
                return el.find_element(By.CSS_SELECTOR, selector).get_attribute(attr)
            except:
                return ""

        wait = WebDriverWait(self, 10)

        try:
            hotel_boxes = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="list"][data-results-container="1"]')
                )
            )

            hotel_cards = self.find_elements(
                By.CSS_SELECTOR, 'div[data-testid="property-card"]'
            )
            print("Loaded property cards:", len(hotel_cards))

            while len(hotel_cards) < total_properties:
                # Scroll to the bottom of the page
                self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait for the new content to load; adjust sleep time if necessary
                time.sleep(4)

                # Check if the "Load more results" button exists and click it if present.
                try:
                    load_more_button = self.find_element(
                        By.XPATH,
                        "//button[.//span[contains(text(), 'Load more results')]]",
                    )
                    if load_more_button:
                        load_more_button.click()
                        print("loading more cards...")
                        # Optionally wait a bit after clicking
                        time.sleep(4)
                except:
                    print(f"load more button not found")

                hotel_cards = self.find_elements(
                    By.CSS_SELECTOR, 'div[data-testid="property-card"]'
                )
                print("Loaded property cards:", len(hotel_cards))

            # List to hold all rows
            rows = []
            for i, card in enumerate(hotel_cards, 1):
                # Extract entire review block as a single string
                review_block = safe_find_text(card, '[data-testid="review-score"]')

                # Initialize defaults
                review_score = ""
                review_label = ""
                review_count = ""

                # Split by lines and parse
                if review_block:
                    lines = review_block.split("\n")
                    if len(lines) == 4:
                        # Sometimes label is duplicated, use 2nd and 3rd
                        review_score = lines[1]
                        review_label = lines[2]
                        review_count = lines[3]
                    elif len(lines) == 3:
                        review_score, review_label, review_count = lines
                    elif len(lines) == 2:
                        review_label, review_count = lines
                    elif len(lines) == 1:
                        review_label = lines[0]

                # Clean review count
                review_count = review_count.replace(",", "").replace(" reviews", "")

                hotel = {
                    "Title": safe_find_text(card, '[data-testid="title"]'),
                    "Address": safe_find_text(card, '[data-testid="address"]'),
                    "Distance from Centre": safe_find_text(
                        card, '[data-testid="distance"]'
                    ),
                    "Review Score": review_score,
                    "Review Label": review_label,
                    "Review Count": review_count,
                    "Price": safe_find_text(
                        card, '[data-testid="price-and-discounted-price"]'
                    ).replace("\n", " "),
                    "Taxes and Charges": safe_find_text(
                        card, '[data-testid="taxes-and-charges"]'
                    ),
                    "Booking Link": safe_find_attr(
                        card, 'a[data-testid="title-link"]', "href"
                    ),
                    "Image URL": safe_find_attr(
                        card,
                        'a[data-testid="property-card-desktop-single-image"] img',
                        "src",
                    ),
                }
                rows.append(hotel)

            df = pd.DataFrame(rows)
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(
                f"{output_dir}/hotels.csv", index=False, encoding="utf-8", quoting=1
            )

            print("\n✅ Data saved to hotels.csv")

        except Exception as e:
            print(f"[❌ ERROR getting hotel cards] {e}")
            return []
