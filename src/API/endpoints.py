from flask import Blueprint, jsonify
from scraping_code import BASE_URL, get_all_solved_links, get_user_stats, get_submissions_details, multiple_threads_scraping

endpoints = Blueprint('endpoints', __name__)


@endpoints.route('/')
def root():
    data = {
        'message': 'Welcome to codechefAPI, this api is for educational purpose only',
        'endpoints': {
            'user-stats/<user_profile_name>': 'return user profile data details',
            'solved/<user_profile_name>': 'return user all solved question links',
            'submission-details/<user_profile_name>': 'return details from submission graph',
            'contest-details/<user_profile_name>': 'return user all contest participation details'
        }
    }
    return jsonify(data)


@endpoints.route('/user-stats/<string:user_stats_user_name>')
def user_stats(user_stats_user_name):
    data = get_user_stats(user_stats_user_name)
    return jsonify(data)


@endpoints.route('/solved/<string:solved_question_user_name>')
def solved_question(solved_question_user_name):
    res = get_all_solved_links(solved_question_user_name, 'api')
    total_links = 0
    links = []

    if res['status'] != 200:
        return jsonify({
            'status': res['status'],
            'message': res['message']
        })

    for link in res['links']:
        links.append(BASE_URL + link.get('href'))
        total_links += 1
        
    return jsonify({'total_solved': total_links, 'solved_links': links})


@endpoints.route('/submission-details/<string:submission_details_user_name>')
def submission_details(submission_details_user_name):
    details = get_submissions_details(submission_details_user_name)
    return jsonify(details)


@endpoints.route('/contest-details/<string:contest_details_user_name>')
def contest_details(contest_details_user_name):
    details = multiple_threads_scraping(contest_details_user_name)
    return jsonify(details)
