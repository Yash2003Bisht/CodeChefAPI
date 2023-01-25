import random
import time
import requests
from typing import Any
from bs4 import BeautifulSoup
from user_agents import USER_AGENTS

BASE_URL = 'https://www.codechef.com'
MAX_RETIRES = 5
MIN_TIME_SLEEP = 15  # in seconds
MAX_TIME_SLEEP = 45  # in seconds


def get_response(url: str, r_type: Any = 'soup', custom_headers: dict = None):
    """Make a get request to url

    Args:
        url (str): profile url on codechef
        r_type (str): return type json or soup object, default return type is soup
        custom_headers (dict): custom headers you want to send

    Returns:
        Any: if r_type is soup then (bs4.BeautifulSoup)BeautifulSoup object to parse the HTML were return otherwise json
    """
    # loop to retry the request for MAX_RETRIES times
    for _ in range(MAX_RETIRES):
        try:

            if custom_headers is None:
                custom_headers = {}

            custom_headers['user-agent'] = random.choice(USER_AGENTS)['User-Agent']
            res = requests.get(url, timeout=120, headers=custom_headers)

            # check if the request is successful
            if res.ok:

                if r_type == 'soup':
                    soup = BeautifulSoup(res.content, 'html.parser')
                    return soup

                else:
                    return res.json()

            else:
                print(f'\nBad status code -> {res.status_code}')
                time.sleep(random.randrange(MIN_TIME_SLEEP, MAX_TIME_SLEEP))

        except Exception as err:
            print(f'\nerror -> {err}')
            time.sleep(random.randrange(MIN_TIME_SLEEP, MAX_TIME_SLEEP))

    # return None if soup object or json is not returned after MAX_RETRIES
    return None


def get_clean_code(code: str):
    """Remove unnecessary \n from the code

    Args:
        code (str): text code

    Returns:
        str: clean code
    """
    for i in range(len(code)):
        if code[i] != '\n':
            code = code[i:]
            break

    return code
