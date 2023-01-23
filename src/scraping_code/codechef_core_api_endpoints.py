from src.helper_functions import get_response


def submission_endpoint(question_tag: str, username: str):
    """Codechef submission details endpoint

    Args:
        question_tag (str): unique question tag
        username (str): profile name on codechef

    Returns:
        _type_: _description_
    """
    url = f"https://www.codechef.com/api/submissions/PRACTICE/{question_tag}?limit=20&page=0&language=&status=&usernames={username}"
    headers = {
        "authority": "www.codechef.com",
        "method": "GET",
        "path": f"/api/submissions/PRACTICE/{question_tag}?limit=20&page=0&language=&status=&usernames={username}",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-GB,en;q=0.5",
        "cookie": "SESS93b6022d778ee317bf48f7dbffe03173=23eb3d6c660fd61f83b01aafcef51d38; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb2RlY2hlZi5jb20iLCJzdWIiOiIzNTg2NzkyIiwidXNlcm5hbWUiOiJjYXJsczU2NyIsImlhdCI6MTY3NDQwMDkwMCwibmJmIjoxNjc0NDAwOTAwLCJleHAiOjE2NzYzOTUzMDB9.mss0ARTCT6RWMwKJmbMNGYIF0qh4z-3RoTCboM4oGTE; uid=3586792",
        "referer": f"https://www.codechef.com/status/{question_tag}?limit=20&page=0&usernames={username}&language=&status=",
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

    res_data = get_response(url, "json",headers)
    details = []

    if res_data is not None:
        for data in res_data['data']:
            details.append({
                'solution_id': data['id'],
                'lang': data['language'],
                'status': data['tooltip'],
                'execution_time': data['time'],
                'memory': data['memory']
            })

        return details

    return None


if __name__ == "__main__":
    print(submission_endpoint("MANAPTS", "yash2003bisht"))
