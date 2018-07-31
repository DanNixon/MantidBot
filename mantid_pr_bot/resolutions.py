import json

from random import randrange
from string import Template


def get_admins(pr):
    """
    Gets a list of admins to be notified for unexpected or edge case
    situations.

    @return Gatekeepers
    """
    return ['mantidproject/gatekeepers']


def get_pr_developer(pr):
    """
    Gets the developer of a pull request.

    The developer is either the author of the last commit (if the author and
    committer are the same) or the author and committer if they are different
    (and rely on human judgement then they are both notified).

    @return Single element list containing current developer
    """
    try:
        author = pr['commits']['nodes'][0]['commit']['author']['user']['login']
        committer = pr['commits']['nodes'][0]['commit']['committer']['user']['login']
        return [author] if author == committer else [author, committer]
    except TypeError:
        return []


def get_pending_reviewers(pr):
    """
    Gets a list of all users that have yet to complete a review (i.e. they have
    started one or been assigned to provide one but are yet to complete one).

    @return List of usernames of pending review authors.
    """
    return [r['author']['login'] for r in pr['reviews']['nodes'] if r['state'] == 'PENDING']


def get_requested_reviewers(pr):
    """
    Gets a list of users who have outstanding review requests on a pull
    request.

    @return List of users from which reviews are requested
    """
    return [rr['requestedReviewer']['login'] for rr in pr['reviewRequests']['nodes']]


resolutions = {
    'generic': (get_admins, [
        Template('$users can you take a look at this?'),
        Template('$users it looks like there are some issues here, can you investigate?')
    ]),
    'no_dev': (get_admins, [
        Template('$users this PR is now without a developer.')
    ]),
    'conflicting': (get_pr_developer, [
        Template('$users there are conflicts here, can you resolve them.')
    ]),
    'failing': (get_pr_developer, [
        Template('$users the build is failing, can you investigate.'),
        Template('$users have you had a chance to see why the build is failing?')
    ]),
    'unreviewed': (get_pr_developer, [
        Template('$users do you want to request a review on this PR?'),
        Template('$users it may be worth bringing this PR to attention for review.')
    ]),
    'pending_review': (get_pending_reviewers, [
        Template('$users have you had a chance to complete your review yet?'),
        Template('$users do you have any comments on this PR?')
    ]),
    'pending_gatekeeper': (get_admins, [
        Template('$users this looks good, is it time for the second review?'),
        Template('$users do you have a moment to give this a look over?')
    ]),
    'review_requested': (get_requested_reviewers, [
        Template('$users have you had a chance to complete your review yet?'),
        Template('$users do you have any comments on this PR?')
    ]),
    'ignored_review': (get_pr_developer, [
        Template('$users have you had a chance to look at the review comments yet?'),
        Template('$users could you review the feedback left on this PR and make '
                 'changes as appropriate'),
    ])
}


def fill_message_template(template, usernames):
    """
    Fills a message template with a list of usernames.

    @template Comment string template
    @usernames Single string or list of strings containing usernames
    @return Comment text
    """
    if not isinstance(usernames, list):
        usernames = [usernames]

    user_str = ', '.join(['@{}'.format(u.strip()) for u in usernames])
    msg_str = template.substitute(users=user_str)

    return msg_str


def fill_random_response_message(problem_type, pr):
    """
    Selects and generates a random comment text for a PR, extracting the
    relevant users to be notified.

    @param problem_type Type of problem message desired
    @param pr Pull request to process
    @return Comment text
    """
    if problem_type not in resolutions.keys():
        problem_type = 'generic'

    usernames = resolutions[problem_type][0](pr)
    idx = randrange(0, len(resolutions[problem_type][1]))
    user_msg = fill_message_template(resolutions[problem_type][1][idx], usernames)

    machine_msg = json.dumps({'problem_type': problem_type})

    msg_str = '{}\n<!-- {} -->'.format(user_msg, machine_msg)

    return msg_str


def generate_resolution_comments(sorted_prs):
    """
    Generates a resolution comment for each sorted pull request.

    @param sorted_prs Dictionary of response type to list of pull requests
    @return List of (pull request, comment text) tuples
    """
    comments = []
    for problem_type, prs in sorted_prs.items():
        comments.extend(
                [(pr, fill_random_response_message(problem_type, pr)) for pr in prs])
    return comments
