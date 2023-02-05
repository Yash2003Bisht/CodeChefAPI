from helper_functions import get_response
from typing import Any

headers = {
    "authority": "www.codechef.com",
    "method": "GET",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.5",
    "cookie": "SESS93b6022d778ee317bf48f7dbffe03173=23eb3d6c660fd61f83b01aafcef51d38; \
               Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb2RlY2hlZi5jb20iLCJzdWIiOiIzNTg2NzkyIiwidXNlcm5 \
               hbWUiOiJjYXJsczU2NyIsImlhdCI6MTY3NDQwMDkwMCwibmJmIjoxNjc0NDAwOTAwLCJleHAiOjE2NzYzOTUzMDB9. \
               mss0ARTCT6RWMwKJmbMNGYIF0qh4z-3RoTCboM4oGTE; uid=3586792",
    "sec-ch-ua": '"Not_A Brand";v="99", "Brave";v="109", "Chromium";v="109"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "x-csrf-token": "177441ba8e67aea30b500b160b81625cf311b596252b18e03a27c9556a446d93",
    "x-requested-with": "XMLHttpRequest"
}


def contest_endpoint(contest_name: str, username: str) -> Any:
    """Codechef contest details endpoint

    Args:
        contest_name (str): contest name on codechef
        username (str): profile name on codechef

    Returns:
        dict or None: return a dictionaries if the request is successful, otherwise, return None
    """
    url = f"https://www.codechef.com/api/rankings/{contest_name}?itemsPerPage=100&order=asc&page=1&search={username}&sortBy=rank"

    # add aditional details
    headers["path"] = f"/api/rankings/{contest_name}?itemsPerPage=100&order=asc&page=1&search={username}&sortBy=rank"
    headers[
        "referer"] = f"https://www.codechef.com/rankings/{contest_name}?itemsPerPage=100&order=asc&page=1&search={username}&sortBy=rank"

    res_data = get_response(url, "json", headers)
    details = {}

    if res_data is not None:
        details['contest_code'] = res_data['contest_info']['contest_code']
        details['contest_name'] = res_data['contest_name']
        details['rank'] = res_data['list'][0]['rank']
        details['total_score'] = res_data['list'][0]['score']

        problems_solved = {}
        total_problems = []
        total_solved = 0

        for key, value in res_data['list'][0]["problems_status"].items():
            problems_solved[key] = value
            problems_solved[key]['question_link'] = f"https://www.codechef.com/LP1TO201/problems/{key}"
            problems_solved[key]['submission_link'] = \
                f"https://www.codechef.com/rankings/{contest_name}/bestsolution/{key},{username}"
            total_solved += 1

        for problem in res_data['problems']:
            data = problem
            data['question_link'] = f"https://www.codechef.com/LP1TO201/problems/{data['code']}"
            total_problems.append(data)

        details['problems_solved'] = problems_solved
        details['total_problems'] = total_problems
        details['total_solved'] = total_solved

        return details

    return None


if __name__ == "__main__":
    print(contest_endpoint("LP1TO201", "yash2003bisht"))
