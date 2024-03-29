# CodeChefAPI
With CodeChef API you can get stats, contest details, all solved question links, and submission details for any user.

## Endpoints
1. user-stats
2. contest-details
3. solved
4. submission-details

### user-stats
Returns brief details about the user, such as the total number of contests participated, country, division, global rank, etc.

#### sample code
```pycon
import requests

url = "http://localhost:5000/user-stats"
res = requests.post(url, headers={"username": "yash2003bisht"})
print(res.json())
```

#### sample response
```json lines
{
    "badges": {
        "1v1_challenge_badge": "bronze_badge",
        "daily_streak": "gold_badge",
        "problem_solver": "silver_badge"
    },
    "codechef_pro_plan": "No Active Plan",
    "contest_participate": 5,
    "country": "India",
    "country_rank": 84362,
    "discuss_profile": "https://discuss.codechef.com/u/yash2003bisht",
    "division": "(Div 4)",
    "global_rank": 90654,
    "link": "https://yash2003bisht.github.io/",
    "problem_fully_solved": 444,
    "problem_partially_solved": 0,
    "rating": 1279,
    "student/professional": "Other",
    "teams_list": "https://www.codechef.com/users/yash2003bisht/teams",
    "total_stars": 1,
    "username": "yash2003bisht"
}
```

### contest-details
Returns all details about user contests participated.

#### sample code
```pycon
import requests

url = "http://localhost:5000/contest-details"
res = requests.post(url, headers={"username": "yash2003bisht"})
print(res.json())
```

#### sample response
```json lines
{
  "contest_details": [
    {
      "START51D": [
        "https://www.codechef.com/START51D/status/POPULATION,yash2003bisht",
        "https://www.codechef.com/START51D/status/TVDISC,yash2003bisht",
        "https://www.codechef.com/START51D/status/DOMINANT2,yash2003bisht"
      ],
      "rank": 4809,
      "score": 300.0
    },
    {
      "AUG221D": [
        "https://www.codechef.com/AUG221D/status/MAXIMUMSUBS,yash2003bisht",
        "https://www.codechef.com/AUG221D/status/SALESEASON,yash2003bisht",
        "https://www.codechef.com/AUG221D/status/EQUALISE,yash2003bisht",
        "https://www.codechef.com/AUG221D/status/TWOTRAINS,yash2003bisht",
        "https://www.codechef.com/AUG221D/status/SMALLXOR,yash2003bisht",
        "https://www.codechef.com/AUG221D/status/HLEQN,yash2003bisht"
      ],
      "rank": 345,
      "score": 600.0
    }
  ],
  "total_contest": 2,
  "total_scraped": 2
}
```

### solved
Returns a list of links containing all questions solved by user.

#### sample code
```pycon
import requests

url = "http://localhost:5000/solved"
res = requests.post(url, headers={"username": "yash2003bisht"})
print(res.json())
```

#### sample response
```json lines
{
  "solved_links": [
    "https://www.codechef.com/status/FLOW006?usernames=yash2003bisht"
  ],
  "total_solved": 1
}
```

### submission-details
Returns data from the submissions graph section.

#### sample code
```pycon
import requests

url = "http://localhost:5000/submission-details"
res = requests.post(url, headers={"username": "yash2003bisht"})
print(res.json())
```

#### sample response
```json lines
{
  "compile_error": 1,
  "runtime_error": 25,
  "solutions_accepted": 384,
  "solutions_partially_accepted": 5,
  "time_limit_exceeded": 15,
  "wrong_answer": 104
}
```

*Note*: **submission-details** endpoints may take a longer time to fetch data, as there is some animation in data that delays loading graph details, so we are using **selenium** to scrape it.
