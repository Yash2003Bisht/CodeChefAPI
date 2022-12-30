import re
import time
from .code_scraper import get_soup_object, BASE_URL
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from bs4 import BeautifulSoup, element
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_driver_object():
    """Selenium webdriver object

    Returns:
        WebDriver (selenium.webdriver.chrome.webdriver.WebDriver): Webdriver object for scraping data
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")  # linux only
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        return driver

    except Exception as err:
        print(f'error -> {err}')
        return None


def get_user_stats(username: str):
    """User Profile Scraper

    Args:
        username (str): user profile name

    Returns:
        JSON: JSON data containing all information about the user profile 
    """
    url = BASE_URL + '/users/' + username
    soup = get_soup_object(url)
    data = {}
    stars = 0

    try:
        ul_tag = soup.find('ul', {'class': 'side-nav'})

        if ul_tag is None:
            return {
                'status': 404,
                'message': 'Invalid username'
            }

    except AttributeError:
        return {
            'status': 500,
            'message': 'Internal server error'
        }

    # profile details like username, country, institution etc.
    for li in ul_tag.find_all('li'):

        try:
            value = li.find('a').get('href')
            if 'profile-plan' in value:
                value = re.sub(" +", " ", li.find('span').get_text().replace('\n', '').encode("ascii",
                                                                                              "ignore").decode()).strip().split(
                    ".")[0]
            elif not value.startswith('https://'):
                value = BASE_URL + value

        except AttributeError:
            value = re.sub(" +", " ",
                           li.find('span').get_text().replace('\n', '').encode("ascii", "ignore").decode()).strip()

        if value[0].isdigit():
            stars = int(value[0])
            data[li.find('label').get_text().lower().replace(" ", "_").replace(":", "")] = value[1:]
        else:
            data[li.find('label').get_text().lower().replace(" ", "_").replace(":", "")] = value

    # badges
    widgets = soup.find_all('p', {'class': 'badge__title'})
    badges = {}

    try:
        for widget in widgets:
            badge_name, badge = widget.get_text().split('-')
            badges.update({badge_name.strip().lower().replace(' ', '_'): badge.strip().lower().replace(' ', '_')})

    except ValueError:
        badges = widgets[0].get_text()

    except Exception as err:
        print(err)
        badges = 'Internal server error'

    rating_header = soup.find_all('div', {'class': 'rating-header text-center'})[0].find_all('div')
    rating_ranks = soup.find('div', {'class': 'rating-ranks'}).find_all('strong')
    rating_data_section = soup.find('section', {'class': 'rating-data-section problems-solved'})

    temp_global_rank = rating_ranks[0].get_text()
    temp_country_rank = rating_ranks[1].get_text()
    total_problem = rating_data_section.find_all('h5')

    global_rank = int(temp_global_rank) if temp_global_rank.isdigit() else temp_global_rank
    country_rank = int(temp_country_rank) if temp_country_rank.isdigit() else temp_country_rank
    rating = int(rating_header[0].get_text().split("?")[0])
    division = rating_header[1].get_text()
    problem_fully_solved = int(re.findall(r'[0-9]+', total_problem[0].get_text())[0])
    problem_partially_solved = int(re.findall(r'[0-9]+', total_problem[1].get_text())[0])

    try:
        contest_participate = int(len(rating_data_section.find('article').find_all('p')) - 1)
    except AttributeError:
        contest_participate = 0

    data['total_stars'] = stars
    data['rating'] = rating
    data['division'] = division
    data['global_rank'] = global_rank
    data['country_rank'] = country_rank
    data['problem_fully_solved'] = problem_fully_solved
    data['problem_partially_solved'] = problem_partially_solved
    data['contest_participate'] = contest_participate
    data['badges'] = badges

    return data


def get_submissions_details(username):
    """Scrape data from submission graphs using a headless browser, as the chart is loaded dynamically using JavaScript

    Args:
        username (str): user profile name

    Returns:
        dict: submission graph details
    """
    url = BASE_URL + '/users/' + username
    driver = get_driver_object()
    data = {}
    keys = ['compile_error', 'runtime_error', 'time_limit_exceeded', 'wrong_answer', 'solutions_accepted',
            'solutions_partially_accepted']
    total = 0

    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        graph_details = soup.find_all('g', {'class': 'highcharts-data-label'})

        if len(graph_details) == 0:
            return {
                'status': 404,
                'message': 'Invalid username'
            }

    except AttributeError:
        return {
            'status': 500,
            'message': 'Internal server error'
        }

    for index, details in enumerate(graph_details):
        data[keys[index]] = int(details.find('tspan').get_text().encode("ascii", "ignore").decode())
        total += index

    return data


def get_contest_details(username: str, contest: element.Tag):
    """Contest details scraper

    Args:
        username (str): user profile name
        contest (bs4.element.Tag): bs4.element.Tag object
    """
    try:
        contest_name = contest.find('strong').get_text().replace(':', '')

        # selenium scraping
        contest_url = BASE_URL + f'/rankings/{contest_name}?itemsPerPage=100&order=asc&page=1&search={username}&sortBy=rank'
        driver = get_driver_object()

        if driver is None:
            return {}

        driver.get(contest_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td"))
        )

        # additional wait to load the page
        time.sleep(5)

        contest_soup = BeautifulSoup(driver.page_source, "html.parser")
        table_data = contest_soup.find_all('td')

        return {
            contest_name: list(map(lambda a_tag: BASE_URL + a_tag.get('href'), contest.find_all('a'))),
            'rank': int(table_data[0].get_text().replace('Rank', '')),
            'score': float(re.sub(r'\(.*\)', '', table_data[2].get_text().replace('Total Score', ''))),
        }

    except Exception as err:
        print(f'error -> {err}')
        return {}


def multiple_threads_scraping(username: str):
    """Multiple threads scraping for contest details page

    Args:
        username (str): user profile name

    Returns:
        dict: scraped data
    """
    url = BASE_URL + '/users/' + username
    soup = get_soup_object(url)
    data = {}

    try:
        details = soup.find('section', {'class': 'rating-data-section problems-solved'})
        if details is None:
            return {
                'status': 404,
                'message': 'Invalid username'
            }

    except AttributeError:
        return {
            'status': 500,
            'message': 'Internal server error'
        }

    article_tag = details.find('article')

    if article_tag is not None:
        contest_participate = article_tag.find_all('p')[1:]
        total_contest = max(1, len(contest_participate))
        total_scraped = 0
        contest_details = []

        executor = ThreadPoolExecutor(min(10, total_contest))

        for contest_detail in executor.map(get_contest_details, repeat(username), contest_participate):
            if len(contest_detail) > 1:
                contest_details.append(contest_detail)
                total_scraped += 1

    else:
        contest_details = []
        total_contest = 0
        total_scraped = 0

    data['contest_details'] = contest_details
    data['total_contest'] = total_contest
    data['total_scraped'] = total_scraped

    return data
