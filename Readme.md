# CodeChefAPI
The codechef API is for educational purposes only.

## Endpoints
1. user-stats/<user_name>
2. contest-details/<user_name>
3. solved/<user_name>
4. submission-details/<user_name>

### user-stats
Returns brief details about the user, such as the total number of contests participated, country, division, global rank, etc.

#### sample
```json lines
{
  "codechef_pro_plan": "No Active Plan",
  "contest_participate": 2,
  "country": "India",
  "country_rank": 93736,
  "division": "(Div 4)",
  "global_rank": 100753,
  "link": "https://yash2003bisht.github.io/",
  "problem_fullysolved": 206,
  "problem_partiallysolved": 0,
  "rating": 1346,
  "student/professional": "Other",
  "teams_list": "https://www.codechef.com/users/yash2003bisht/teams",
  "total_stars": 1,
  "username": "yash2003bisht"
}
```

### contest-details
Returns all details about user contests participated.
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
```json lines
{
  "solved_links": [
    "https://www.codechef.com/status/TEAMSEL,testing"
  ],
  "total_solved": 1
}
```

### submission-details
Returns data from the submissions graph section.
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

*Note*: The **submission-details** and **contest-details** endpoints may take longer to fetch the data, as the data are loaded dynamically, and we are using selenium to scrape it.
