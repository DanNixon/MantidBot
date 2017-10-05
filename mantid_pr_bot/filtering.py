from datetime import datetime
from functools import partial


def count_reviews(pr):
    return len([r for r in pr['reviews']['nodes'] if r['state'] != 'COMMENTED'])


def has_pr_not_been_updated_since(threshold_days, pr):
    """
    Returns true if the pull request was last updated after a threshold number
    of days.
    """
    ref_time = datetime.strptime(pr['updatedAt'], "%Y-%m-%dT%H:%M:%SZ")
    elapsed_days = (datetime.now() - ref_time).days
    return elapsed_days >= threshold_days


def filter_to_stale_prs(threshold_days, prs):
    """
    Filters the list of pull request to those that are considerd stale.

    @param threshold_days Number of days after which a PR is "stale"
    @param prs List of all pull requests
    @return Iterator over stale pull requests
    """
    f = partial(has_pr_not_been_updated_since, threshold_days)
    return filter(f, prs)


def is_author_of_last_commit_no_longer_a_mantid_dev(pr):
    """
    Returns true if author of last commit is not set or set to the empty
    string.
    """
    try:
        last_commit_author = \
                pr['commits']['nodes'][0]['commit']['author']['user']['login']
        return len(last_commit_author) == 0
    except TypeError:
        return True


def was_ci_status_of_last_pr(status, pr):
    """
    Returns true if the status of the last commit is set to a given status.
    """
    try:
        last_commit_build_result = \
                pr['commits']['nodes'][0]['commit']['status']['state']
    except KeyError:
        last_commit_build_result = ''
    return last_commit_build_result == status


def filter_to_ci_pass(prs):
    """
    Filters the list of pull request to those that passed CI checks on the last
    commit.

    @param prs List of all pull requests
    @return Iterator over succesful pull requests
    """
    f = partial(was_ci_status_of_last_pr, 'SUCCESS')
    return filter(f, prs)


def filter_to_ci_fail(prs):
    """
    Filters the list of pull request to those that failed CI checks on the last
    commit.

    @param prs List of all pull requests
    @return Iterator over failing pull requests
    """
    f = partial(was_ci_status_of_last_pr, 'FAILURE')
    return filter(f, prs)


def does_this_pr_have_merge_conflicts(pr):
    """
    Returns true if this PR has conflicts and cannot be automatically merged.
    """
    return pr['mergeable'] == 'CONFLICTING'


def has_noone_reviewed_this_pr(pr):
    """
    Returns true if there are no reviews and no review requests.
    """
    return count_reviews(pr) == 0 and len(pr['reviewRequests']['nodes']) == 0


def has_a_reviewer_not_reviewed_this_pr(pr):
    """
    Returns true if there are pending reviews (i.e. a reviewer is assigned but
    they are yet to complete the review).
    """
    for r in pr['reviews']['nodes']:
        if r['state'] == 'PENDING':
            return True

    return False


def has_a_gatekeeper_not_reviewed_this_accepted_pr(pr):
    """
    Returns true if all reviews (of which there must be at least one) are
    approved and no review requests are outstanding.
    """
    if count_reviews(pr) == 0 or len(pr['reviewRequests']['nodes']) > 0:
        return False

    for r in pr['reviews']['nodes']:
        if not (r['state'] == 'APPROVED' or r['state'] == 'COMMENTED'):
            return False

    return True


def has_a_requested_reviewer_not_reviewed_this_pr(pr):
    """
    Returns true if there are outstanding review requests.
    """
    return len(pr['reviewRequests']['nodes']) > 0


def has_the_author_not_responded_to_review_comments(pr):
    """
    Returns true if there is at least one review which requested changes.
    """
    for r in pr['reviews']['nodes']:
        if r['state'] == 'CHANGES_REQUESTED':
            return True

    return False
