import os
import sys
import random
import time
import requests
from bs4.element import ResultSet
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

try:
    # for API use
    from .user_headers import USER_AGENTS

except ImportError:
    # for direct use
    from user_headers import USER_AGENTS

LANG = {
    'PYTH 3': 'py',
    'PYTH 2': 'py',
    'PYTH': 'py',
    'C': 'c',
    'C++14': 'cpp',
    'C++17': 'cpp',
    'C++ 4.0.0-8': 'cpp',
    'C++ 4.9.2': 'cpp',
    'C++ 4.3.2': 'cpp',
    'C++11': 'cpp',
    'PAS fpc': 'pp',
    'JAVA': 'java',
    'PYPY3': 'py',
    'PYPY2': 'py',
    'PYPY': 'py',
    'ADA': 'adb',
    'C#': 'cs',
    'NODEJS': 'js',
    'JS': 'js',
    'GO': 'go',
    'KTLN': 'kt',
    'RUBY': 'ruby',
    'rust': 'rs',
}

BASE_URL = 'https://www.codechef.com'
MAX_RETIRES = 5
MIN_TIME_SLEEP = 15  # in seconds
MAX_TIME_SLEEP = 45  # in seconds


def get_soup_object(url: str):
    """Get Soup Object

    Args:
        url (str): profile url on codechef

    Returns:
        bs4.BeautifulSoup: BeautifulSoup object to parse the HTML
    """
    # loop to retry the request for MAX_RETRIES times
    for _ in range(MAX_RETIRES):
        try:
            res = requests.get(url, timeout=120, headers=random.choice(USER_AGENTS))
            soup = BeautifulSoup(res.content, 'html.parser')

            # check if the request is successful
            if res.status_code == 200:
                return soup
            else:
                print(f'Bad status code -> {res.status_code}')
                time.sleep(random.randrange(MIN_TIME_SLEEP, MAX_TIME_SLEEP))

        except Exception as err:
            print(f'\nerror -> {err}')
            time.sleep(random.randrange(MIN_TIME_SLEEP, MAX_TIME_SLEEP))

    # return None if soup object is not returned after MAX_RETRIES
    return None


def get_all_solved_links(username: str, usage: str) -> dict:
    """User all solved question links

    Args:
        username (str): profile name on codechef
        usage (str): using as API or direct

    Returns:
        dict: contains two value status and links(all un-scraped link list)/message
    """
    url = f'{BASE_URL}/users/{username}'
    soup = get_soup_object(url)
    links = []

    try:
        # get all solved questions links
        anchor_tag = soup.find('section', {'class': 'rating-data-section problems-solved'})

        if anchor_tag is None:
            if usage == 'api':
                return {
                    'status': 404,
                    'message': 'Invalid username'
                }

            else:
                print('Invalid username')
                quit()

        links = anchor_tag.find_all('a')

    except AttributeError:
        if usage == 'api':
            return {
                'status': 500,
                'message': 'Internal server error'
            }

        else:
            print('max retries reached')
            quit()

    if usage == 'normal':
        base_dir = 'solutions'

        if len(links) == 0:
            return {
                'links': [],
                'no_solution_found': True
            }

        if os.path.exists(base_dir):
            # list all the files in the solutions directory
            already_scraped = os.listdir(base_dir)

            # filter out the already scraped link
            links = list(filter(lambda link: link.get_text() not in already_scraped, links))

    return {
        'status': 200,
        'links': links
    }


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


def save_solution(question: str, lang: str, solution_id: str, status: str, execution_time: str, memory: str):
    """Function is used to save the text of a specific solution to a file.

    Args:
        question (str): name of the question the solution is for
        lang (str): programming language used in the solution
        solution_id (str): the id of the solution
        status (str): status of the solution (e.g. 'accepted', 'wrong answer', 'runtime error', etc.)
        execution_time (str): execution time of the solution
        memory (str): memory usage of the solution
    """
    url = f'{BASE_URL}/viewplaintext/{solution_id}'
    soup = get_soup_object(url)
    comment_symbol = '//'

    # comment symbols for PAS fpc -> pp
    comment_symbol_start = '{'
    comment_symbol_end = '}'

    try:
        text = get_clean_code(soup.get_text())
        lang = LANG[lang]

        # save all scraped solution to "solutions" dir
        base_dir = 'solutions'
        path = os.path.join(base_dir, question)

        if not os.path.exists(path):
            os.makedirs(path)

        if lang == 'py':
            comment_symbol = '#'
        elif lang == 'adb':
            comment_symbol = '--'

        total = len(os.listdir(path)) + 1

        with open(f'{path}/{question}_{total}.{lang}', 'w') as file:
            if lang == 'pp':
                file.write(
                    f'{comment_symbol_start} QUESTION URL: {BASE_URL}/problems/{question} {comment_symbol_end}\n'
                    f'{comment_symbol_start} STATUS: {status} {comment_symbol_end}\n'
                    f'{comment_symbol_start} TIME: {execution_time} {comment_symbol_end}\n'
                    f'{comment_symbol_start} MEMORY: {memory} {comment_symbol_end}\n\n'
                    f'{text}'
                )
            else:
                file.write(
                    f'{comment_symbol} QUESTION URL: {BASE_URL}/problems/{question}\n'
                    f'{comment_symbol} STATUS: {status}\n'
                    f'{comment_symbol} TIME: {execution_time}\n'
                    f'{comment_symbol} MEMORY: {memory}\n\n'
                    f'{text}'
                )

        return True

    except AttributeError:
        print(f'\nAttributeError')
        return False

    except KeyError as err:
        print(f'\nKeyError for -> {err}')
        return False

    except Exception as err:
        print(f'\nerror -> {err}')
        return False


def scrape_and_save(solution_details: ResultSet):
    """Retrieves the details of a specific solution of a Codechef problem.

    Args:
        solution_details (ResultSet): contains information about a specific solution.

    Returns:
        int: 1 if solution details are successfully scraped and saved, else 0.
    """
    try:
        url = BASE_URL + solution_details.get('href')
        soup = get_soup_object(url)
        tr = soup.find('tbody').find_all('tr')
        solution_scraped = False

        if tr is None:
            return 0

        for row in tr:
            col = row.find_all('td')
            solution_scraped = save_solution(solution_details.get_text(), col[6].get_text(),
                                             col[0].get_text(), col[3].find('span')['title'],
                                             col[4].get_text(), col[5].get_text())

        return 1 if solution_scraped else 0

    except AttributeError:
        return 0


def main(username: str):
    """Main function for scraping Codechef solutions for a specific user.

    Args:
        username (str): profile name on codechef.

    Returns:
        None
    """
    res: dict = get_all_solved_links(username, 'normal')
    total_links: int = len(res['links'])
    executor = ThreadPoolExecutor(max(1, total_links))
    scraped = 0  # variable to take track of total solution scraped

    if res.get('no_solution_found'):
        print('No Solution Found')
        quit()

    elif total_links == 0:
        print('All solution already scraped')
        quit()

    print(f'total solution found: {total_links}')
    sys.stdout.write(f'\r scraped {scraped}/{total_links}')

    for data in executor.map(scrape_and_save, res['links']):
        scraped += data
        sys.stdout.write(f'\r scraped {scraped}/{total_links}')

    if scraped == total_links:
        print('\nAll solution scraped')
    else:
        print('\nSomething went Wrong')


if __name__ == '__main__':
    main('testing')
