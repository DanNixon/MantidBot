import click

from .github import GitHubClient
from .workflow import filter_prs
from .resolutions import generate_resolution_comments


@click.command()
@click.option('--token', type=str, required=True,
              help='GitHub Personal Access token.')
@click.option('--stale-days', type=int, default=14,
              help='GitHub Personal Access token.')
@click.option('--org', type=str, default='mantidproject',
              help='User/Organisation that owns the repository.')
@click.option('--repo', type=str, default='mantid',
              help='Repository to operate on.')
@click.option('--list-prs', is_flag=True,
              help='List the PRs in each problem category.')
@click.option('--list-comments', is_flag=True,
              help='List the chosen comments for each PR.')
@click.option('--do-commenting', is_flag=True,
              help='Apply the chosen comments to each PR.')
@click.option('--force', is_flag=True,
              help='Skip confirmation prompts')
def main(token, stale_days, org, repo, list_prs, list_comments, do_commenting, force):
    """
    Tool used to gently remind people when a pull request goes stale.

    Pull requests are sorted into several problem categories, each category
    notified the relevant people in a comment of what needs to be done to keep
    the review process ticking over.

    There are several possible comment messages for each problem category to
    add a little variety (therefore note that the output of --list-comments is
    not necessarily the comment that will be posted by --do-commenting in
    separate invocations).
    """
    gh_client = GitHubClient(token, org, repo)

    all_prs = gh_client.fetch_pull_requests()
    prs = filter_prs(all_prs, stale_days)

    # List all PRs in each category
    if list_prs:
        click.echo('Sorted pull requests:')
        for name, prs in prs.items():
            click.echo('{} ({})'.format(name, len(prs)))
            for pr in prs:
                click.echo(' - #{} ({})'.format(pr['number'], pr['url']))
        click.echo()

    # Generate the list of comments
    comments = None
    if list_comments or do_commenting:
        comments = generate_resolution_comments(prs)

    # Print the list of comments for review
    if list_comments:
        click.echo('All comments ({}):'.format(len(comments)))
        for c in comments:
            click.echo('#{} ({})'.format(c[0]['number'], c[0]['url']))
            click.echo('\t{}'.format(c[1]))
        click.echo()

    # Post comments on pull requests
    if do_commenting:
        if force or click.confirm('This will post several comments under the '
                                  'owner of --token, do you want to continue?'):
            click.echo('Posting comments')
            # TODO
        else:
            click.echo('Commenting was cancelled!')
