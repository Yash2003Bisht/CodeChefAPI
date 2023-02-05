from flask import Blueprint, jsonify, request
from scraping_code import BASE_URL, get_all_solved_links, get_user_stats, get_submissions_details, \
    multiple_threads_scraping

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


@endpoints.route('/user-stats', methods=['POST'])
def user_stats():
    username = request.headers.get('username')

    if username is not None:
        data = get_user_stats(username)
        return jsonify(data), data.get('status')

    return jsonify({
        'message': 'username not found'
    }), 400


@endpoints.route('/solved', methods=['POST'])
def solved_question():
    username = request.headers.get('username')

    if username:
        res = get_all_solved_links(username)
        total_links = 0
        links = []

        if res['status'] != 200:
            return jsonify({
                'status': res['status'],
                'message': res['message']
            }), res.get('status')

        for link in res['links']:
            links.append(BASE_URL + link.get('href'))
            total_links += 1

        return jsonify({'total_solved': total_links, 'solved_links': links}), res.get('status')

    return jsonify({
        'message': 'username not found'
    }), 400


@endpoints.route('/submission-details', methods=['POST'])
def submission_details():
    username = request.headers.get('username')

    if username is not None:
        details = get_submissions_details(username)
        return jsonify(details), details.get('status')

    return jsonify({
        'message': 'username not found'
    }), 400


@endpoints.route('/contest-details', methods=['POST'])
def contest_details():
    username = request.headers.get('username')

    if username is not None:
        details = multiple_threads_scraping(username)
        return jsonify(details), details.get('status')

    return jsonify({
        'message': 'username not found'
    }), 400
