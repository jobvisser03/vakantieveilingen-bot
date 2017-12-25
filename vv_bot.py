#!/Users/jobvisser/anaconda/bin/python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import re
from datetime import datetime
import time
import optparse


def is_logged_in(driver):
    if driver.find_elements_by_link_text("Uitloggen"):
        return True
    return False


# go to login page and login
def login(driver, username, password):
    if is_logged_in(driver):
        print('Already logged in')
        return True
    else:
        driver.get('https://www.vakantieveilingen.nl/login.html?backUrl=%2F')
        driver.save_screenshot("pre.png")
        time.sleep(2)
        driver.find_element_by_name('login').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_name('password').send_keys(Keys.RETURN)
        time.sleep(2)
        print('Logged in successfully')
        return True


def countdown(url_auction, offset_seconds):
    # get the expiring time using requests
    # because the element is hidden and changes name dynamically
    r = requests.get(url_auction)
    dt = re.search(r"tsExpires\">(.........................)<", r.text)
    expires = str(dt.group(1))
    exp = datetime.strptime(''.join(expires.rsplit(':', 1)), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
    print('Auction deadline: {}'.format(exp))
    now = datetime.now()
    to_go = (exp - now).total_seconds()

    # don't proceed until the last offset seconds
    while to_go > offset_seconds:
        now = datetime.now()
        to_go = (exp - now).total_seconds()
        print("{} seconds to go".format(to_go))
        time.sleep(0.1)
    return True


def main():
    """
    Vakantieveilingen bot mostly wins.
    """

    p = optparse.OptionParser()
    p.add_option('--username', '-u', default="")
    p.add_option('--password', '-p', default="")
    p.add_option('--max-price', '-m', default="")
    p.add_option('--url-auction', '-a', default="")

    options, arguments = p.parse_args()

    if options.url_auction is '':
        p.error('Auction URL not given')

    if (options.username is '') or (options.password is ''):
        p.error('Username and/or password not given')

    if options.max_price is '':
        p.error('Maximum price not given')

    # parse options
    url_auction = str(options.url_auction)
    username = str(options.username)
    password = str(options.password)
    max_price = int(options.max_price)

    # amount of euro to be bid over the highest amount
    over_bid = 2
    # seconds before deadline when the highest current bid is evaluated
    offset_seconds = 0.75

    # make sure the selenium firefox docker is running:
    # docker run -it -p 4444:4444 selenium/standalone-firefox
    driver = webdriver.Remote(command_executor='http://0.0.0.0:4444/wd/hub',
                            desired_capabilities=DesiredCapabilities.FIREFOX)

    # login to vakantieveilingen
    login(driver, username, password)

    # go to auction page
    driver.get(url_auction)
    time.sleep(2)

    # get all static html elements before countdown
    bid_input_elem = driver.find_element_by_xpath("//*[@class='bid-input']")
    bid_button_elem = driver.find_element_by_xpath("//*[@class='btn btn-orange']")

    # countdown until 0.75 seconds before the deadline
    # setting depends on bandwidth
    countdown(url_auction, offset_seconds)

    # get highest bid
    bid_elem = driver.find_element_by_xpath("//*[@class='jsBidAmountUpdate highest-bid']")
    bid = int(bid_elem.text)
    print("highest bid: {}".format(bid))

    # place higest bid + 2 EUR
    # to avoid losing from a +1 bidder in the last 0.75 seconds
    if int(bid) < max_price:
        bid_input_elem.send_keys(str(bid + over_bid))
        bid_button_elem.click()
        time.sleep(1)
        driver.save_screenshot("your_bid.png")


if __name__ == '__main__':
    main()
