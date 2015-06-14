"""GoEuro selenium tests"""

import unittest
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


class TestFlightResults(unittest.TestCase):
    """Test results on flight results page"""
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.get('http://www.goeuro.de/')

    def tearDownS(self):
        self.driver.quit()

    def test_flight_sorting_by_price(self):
        """Test flight sorting by price is correct"""
        main_page = MainPage(self.driver)
        main_page.search('Berlin, Deutschland', 'Prag, Tschechien')
        search_results_page = SearchResultsPage(self.driver)
        flight_prices = search_results_page.get_flight_sorted_prices()
        self.assertEqual(flight_prices, sorted(flight_prices))


class BasePage():
    def __init__(self, driver):
        self.driver = driver


class MainPage(BasePage):

    def search(self, departure, arrival):
        self.driver.find_element(*MainPageLocators.FROM).send_keys(departure)
        self.driver.find_element(*MainPageLocators.TO).send_keys(arrival)
        while 'search' not in self.driver.current_url:
            self.driver.find_element(*MainPageLocators.SEARCH).click()


class SearchResultsPage(BasePage):
    
    def get_flight_sorted_prices(self):
        d = self.driver
        flight_prices = []
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.visibility_of_element_located(SearchPageLocators.CURRENCY_BEFORE_COMMA))
        while True:
            currency_before_comma_items = d.find_elements(*SearchPageLocators.CURRENCY_BEFORE_COMMA)
            currency_before_comma = map(lambda elem : elem.text.replace('.', ''),
                                        currency_before_comma_items)
            currency_decimals_items = d.find_elements(*SearchPageLocators.CURRENCY_DECIMALS)
            currency_decimals = map(lambda elem : elem.text,
                                    currency_decimals_items)
            flight_prices_on_page = [float(str(x) + '.' + str(y))
                                     for x, y in zip(currency_before_comma, currency_decimals)]
            flight_prices.extend(flight_prices_on_page)
            if self.check_element(SearchPageLocators.NEXT_FLIGHTS):
                d.find_element(*SearchPageLocators.NEXT_FLIGHTS).click()
                wait.until(EC.staleness_of(currency_before_comma_items[0]))
            else:
                break
        logger = logging.getLogger('logger')
        logger.debug(flight_prices)
        return flight_prices

    def check_element(self, locator):
        try:
            self.driver.find_element(*locator)
        except NoSuchElementException:
            return False
        return True
    
    
class MainPageLocators():
    SEARCH = (By.ID, 'search-form__submit-btn')
    FROM = (By.ID, 'from_filter')
    TO = (By.ID, 'to_filter')


class SearchPageLocators():
    NEXT_FLIGHTS = (By.CSS_SELECTOR, '#results-flight .pagination .next a')
    CURRENCY_BEFORE_COMMA = (By.CSS_SELECTOR, '.price-cell-total .currency-beforecomma')
    CURRENCY_DECIMALS = (By.CSS_SELECTOR, '.price-cell-total span:nth-child(3)')


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger('logger').setLevel(logging.DEBUG)
    unittest.main()
