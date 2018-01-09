from itertools import filterfalse

from .filtering import (
        filter_to_stale_prs,
        filter_to_ci_pass,
        filter_to_ci_fail,
        is_author_of_last_commit_no_longer_a_mantid_dev,
        does_this_pr_have_merge_conflicts,
        has_noone_reviewed_this_pr,
        has_a_reviewer_not_reviewed_this_pr,
        has_a_gatekeeper_not_reviewed_this_accepted_pr,
        has_a_requested_reviewer_not_reviewed_this_pr,
        has_the_author_not_responded_to_review_comments)


def filter_prs(all_prs, stale_days_threshold):
    """
    Sorts/filters pull requests into several "problem categories".

    This function is generally where the modification to select the exact pull
    request desired for each problem category should be done.

    Any new problem categories added need to be added to resolutions.py,
    otherwise the admins will always be the ones to be notified with a very
    generic message.

    @param all_prs List of all pull requests retrieved from GitHub API
    @param stale_days_threshold Number of days of inactivity after which a PR is "stale"
    @return Dictionary of problem type to list of affected pull requests
    """

    prs = {}

    prs['no_dev'] = list(filter(
        is_author_of_last_commit_no_longer_a_mantid_dev, all_prs))

    stale_prs = list(filter_to_stale_prs(stale_days_threshold, all_prs))

    prs['conflicting'] = list(filter(
        does_this_pr_have_merge_conflicts, stale_prs))

    prs['failing'] = list(filter_to_ci_fail(stale_prs))

    stale_passing_prs = list(filter_to_ci_pass(stale_prs))

    prs['unreviewed'] = list(filter(
        has_noone_reviewed_this_pr, stale_passing_prs))

    prs['pending_review'] = list(filter(
        has_a_reviewer_not_reviewed_this_pr, stale_passing_prs))

    prs['pending_gatekeeper'] = list(filter(
        has_a_gatekeeper_not_reviewed_this_accepted_pr, stale_passing_prs))

    prs['review_requested'] = list(filter(
        has_a_requested_reviewer_not_reviewed_this_pr, stale_passing_prs))

    prs['ignored_review'] = list(filter(
        has_the_author_not_responded_to_review_comments, stale_passing_prs))

    return prs
