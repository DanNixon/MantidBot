import click

from .github import GitHubClient
from .filtering import (
        filter_to_stale_prs,
        filter_to_ci_pass,
        filter_to_ci_fail,
        is_author_of_last_commit_no_longer_a_mantid_dev,
        has_noone_reviewed_this_pr,
        has_a_reviewer_not_reviewed_this_pr,
        has_a_gatekeeper_not_reviewed_this_accepted_pr,
        has_a_requested_reviewer_not_reviewed_this_pr,
        has_the_author_not_responded_to_review_comments)


@click.command()
@click.option('--token', type=str, required=True)
@click.option('--org', type=str, default='mantidproject')
@click.option('--repo', type=str, default='mantid')
@click.option('--list-prs/--no-list-prs', default=False)
@click.option('--generate-comments/--no-generate-comments', default=False)
@click.option('--do-commenting/--no-do-commenting', default=False)
def main(token, org, repo, list_prs, generate_comments, do_commenting):
    gh_client = GitHubClient(token, org, repo)

    prs = {}

    all_prs = gh_client.fetch_pull_requests()
    stale_prs = list(filter_to_stale_prs(1, all_prs))

    prs['no_dev'] = list(filter(is_author_of_last_commit_no_longer_a_mantid_dev, stale_prs))
    prs['failing'] = list(filter_to_ci_fail(stale_prs))

    stale_passing_prs = list(filter_to_ci_pass(stale_prs))

    prs['unreviewed'] = list(filter(has_noone_reviewed_this_pr, stale_passing_prs))
    prs['pending_review'] = list(filter(has_a_reviewer_not_reviewed_this_pr, stale_passing_prs))
    prs['pending_gatekeeper'] = list(filter(has_a_gatekeeper_not_reviewed_this_accepted_pr, stale_passing_prs))
    prs['review_requested'] = list(filter(has_a_requested_reviewer_not_reviewed_this_pr, stale_passing_prs))
    prs['ignored_review'] = list(filter(has_the_author_not_responded_to_review_comments, stale_passing_prs))

    if list_prs:
        for name, prs in prs.items():
            click.echo('{} ({})'.format(name, len(prs)))
            for pr in prs:
                click.echo(' - #{} ({})'.format(pr['number'], pr['url']))

    comments = []
    if generate_comments or do_commenting:
        # generate comments
        pass

    if generate_comments:
        # print comments
        pass

    if do_commenting:
        # post comments
        pass


if __name__ == '__main__':
    main()
