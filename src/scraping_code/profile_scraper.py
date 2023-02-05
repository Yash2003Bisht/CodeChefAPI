import re
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from bs4 import BeautifulSoup, element
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from scraping_code.codechef_core_api_endpoints import contest_endpoint
from helper_functions import get_response, BASE_URL


def get_all_solved_links(username: str) -> dict:
    """User all solved question links

    Args:
        username (str): profile name on codechef

    Returns:
        dict: contains two value status and links(all un-scraped link list) or message
    """
    url = f'{BASE_URL}/users/{username}'
    soup = get_response(url)

    try:
        # get all solved questions links
        anchor_tag = soup.find('section', {'class': 'rating-data-section problems-solved'})

        if anchor_tag is None:
            return {
                'status': 404,
                'message': 'Invalid username'
            }

        links = anchor_tag.find_all('a')

    except AttributeError:
        return {
            'status': 500,
            'message': 'Internal server error'
        }

    return {
        'status': 200,
        'links': links
    }


def get_driver_object():
    """Selenium webdriver object

    Returns:
        WebDriver (selenium.webdriver.chrome.webdriver.WebDriver): Webdriver object for scraping data using selenium
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")  # linux only
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")

        # driver object
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        return driver

    except Exception as err:
        print(f'error -> {err}')
        return None


def get_user_stats(username: str):
    """Scrapes and returns user profile information from codechef website

    Args:
        username (str): user profile name

    Returns:
        JSON: JSON data containing all information about the user profile 
    """
    url = BASE_URL + '/users/' + username
    soup = get_response(url)
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
    """Scrapes and returns contest details of a user from codechef website

    Args:
        username (str): user profile name
        contest (bs4.element.Tag): bs4.element.Tag object containing contest details

    Returns:
        dict: containing contest name, links of all solved questions, rank and score of the user
    """
    try:
        contest_name = contest.find('strong').get_text().replace(':', '')
        return contest_endpoint(contest_name, username)

    except Exception as err:
        print(f'error -> {err}')
        return {}


def multiple_threads_scraping(username: str):
    """Scrapes contest details of a user using multiple threads.

    Args:
        username (str): user profile name

    Returns:
        dict: containing scraped data, including contest details, the total number of contests participated in and total number of contests scraped.
    """
    url = BASE_URL + '/users/' + username
    soup = get_response(url)
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
        total_contest = len(contest_participate)
        total_scraped = 0
        contest_details = []

        executor = ThreadPoolExecutor(min(10, max(total_contest, 1)))

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
