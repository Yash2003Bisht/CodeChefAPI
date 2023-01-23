import os
import sys
from itertools import repeat
from bs4.element import ResultSet
from concurrent.futures import ThreadPoolExecutor
from src.helper_functions import *
from src.scraping_code.codechef_core_api_endpoints import submission_endpoint

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


def get_all_solved_links(username: str, usage: str) -> dict:
    """User all solved question links

    Args:
        username (str): profile name on codechef
        usage (str): using as API or direct

    Returns:
        dict: contains two value status and links(all un-scraped link list) or message
    """
    url = f'{BASE_URL}/users/{username}'
    soup = get_response(url)
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
    soup = get_response(url)
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


def scrape_and_save(username: str, solution_details: ResultSet):
    """Retrieves the details of a specific solution of a Codechef problem.

    Args:
        username (str): profile name on codechef
        solution_details (ResultSet): contains information about a specific solution.

    Returns:
        int: 1 if solution details are successfully scraped and saved, else 0.
    """
    try:
        solution_scraped = False
        ques_tag = solution_details.get_text()
        submissions = submission_endpoint(ques_tag, username)

        if submissions:
            for submission in submissions:
                solution_scraped = save_solution(ques_tag, submission['lang'], submission['solution_id'],
                                                 submission['status'], submission['execution_time'], submission['memory'])

            return 1 if solution_scraped else 0

        return 0

    except AttributeError:
        return 0


def main(username: str):
    """Main function for scraping Codechef solutions for a specific user.

    Args:
        username (str): profile name on codechef.

    Returns:
        None
    """
    res = get_all_solved_links(username, 'normal')
    total_links = len(res['links'])
    executor = ThreadPoolExecutor(min(10, max(total_links, 1)))
    scraped = 0  # variable to take track of total solution scraped

    if res.get('no_solution_found'):
        print('No Solution Found')
        quit()

    elif total_links == 0:
        print('All solution already scraped')
        quit()

    print(f'total solution found: {total_links}')
    sys.stdout.write(f'\r scraped {scraped}/{total_links}')

    for data in executor.map(scrape_and_save, repeat(username), res['links']):
        scraped += data
        sys.stdout.write(f'\r scraped {scraped}/{total_links}')

    if scraped == total_links:
        print('\nAll solution scraped')
    elif scraped > 0:
        print('\nUnable to scrape all solutions')
    else:
        print('\nUnable to scrape')


if __name__ == '__main__':
    main('yash2003bisht')
