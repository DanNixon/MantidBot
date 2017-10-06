import click

from .github import GitHubClient
from .workflow import filter_prs
from .resolutions import generate_resolution_comments


@click.command()
@click.option('--token', type=str, required=True)
@click.option('--org', type=str, default='mantidproject')
@click.option('--repo', type=str, default='mantid')
@click.option('--list-prs/--no-list-prs', default=False)
@click.option('--list-comments/--no-list-comments', default=False)
@click.option('--do-commenting/--no-do-commenting', default=False)
def main(token, org, repo, list_prs, list_comments, do_commenting):
    gh_client = GitHubClient(token, org, repo)

    all_prs = gh_client.fetch_pull_requests()
    prs = filter_prs(all_prs)

    # List all PRs in each category
    if list_prs:
        for name, prs in prs.items():
            click.echo('{} ({})'.format(name, len(prs)))
            for pr in prs:
                click.echo(' - #{} ({})'.format(pr['number'], pr['url']))

    comments = None
    if list_comments or do_commenting:
        comments = generate_resolution_comments(prs)

    if list_comments:
        for c in comments:
            click.echo('#{} ({})'.format(c[0]['number'], c[0]['url']))
            click.echo('\t{}'.format(c[1]))

    if do_commenting:
        # TODO
        pass


if __name__ == '__main__':
    main()
