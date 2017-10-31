import json
import requests


class GitHubClient(object):
    """
    Class for handling GraphQL queries for GitHub's APIv4.
    """

    def __init__(self, access_token, organisation, repository):
        # GitHub APIv4 endpoint
        self.endpoint = "https://api.github.com/graphql"

        # Create GraphQL Authorization header
        self.auth = {"Authorization": "Bearer {}".format(access_token)}

        # Initialise empty GraphQL variables dictionary
        self.variables = {
                'repo_owner': organisation,
                'repo_name': repository
            }

        # Number of results to return per page
        self.page_size = 25

    def send_query(self, query):
        """
        Sends Query as JSON object, reply formatted as nested python dictionary
        """
        # Read query and variables into JSON formatted string
        message = json.dumps({"query": query, "variables": self.variables})

        # Convert Python None to JSON null
        payload = message.replace("None", "null")

        # Post Query, recieve reply
        reply = requests.post(self.endpoint, payload, headers=self.auth)

        # Return reply as a nested Python dictionary
        return reply.json()

    def fetch_pull_requests(self):
        """
        Gets a list of pull requests.

        Fields that are requested:
            - PR ID (ret[i]['id'])
            - PR number (ret[i]['number'])
            - Time last updated (ret[i]['updatedAt'])
            - GitHub URL (ret[i]['url'])
            - Mergeable state ([ret[i]['mergeable']])
            - Last commit (ret[i]['commits']['nodes'][0])
                - Author's GitHub username (commit['commit']['author']['user']['login'])
                - Committer's GitHub username (commit['commit']['committer']['user']['login'])
                - CI status (commit['commit']['status']['state'])
            - PR reviews (ret[i]['reviews'][j])
                - Status (item['nodes'][i]['state'])
                - Reviewer's GitHub username (item['nodes'][i]['author']['login'])
            - PR review request (ret[i]['reviewRequests'][j])
                - Reviewer's GitHub username (item['nodes'][i]['reviewer']['login'])

        @return List of pull requests with filtered fields
        """
        query = \
            """
            query($repo_owner: String!, $repo_name: String!, $page_size: Int!, $cursor: String){
                repository(owner: $repo_owner, name: $repo_name){
                    pullRequests(first: $page_size, after: $cursor, states: [OPEN]){
                        pageInfo{
                            hasNextPage
                            endCursor
                        }
                        nodes{
                            id
                            number
                            updatedAt
                            url
                            mergeable
                            commits(last: 1){
                                nodes{
                                    commit{
                                        author{
                                            user{
                                                login
                                            }
                                        }
                                        committer{
                                            user{
                                                login
                                            }
                                        }
                                        status{
                                            state
                                        }
                                    }
                                }
                            }
                            reviews(last: 10){
                                nodes{
                                    state
                                    author{
                                        login
                                    }
                                }
                            }
                            reviewRequests(last: 10){
                                nodes{
                                    reviewer{
                                        login
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """

        # Create optional cursor variable (used for pagination)
        self.variables['cursor'] = None
        # Set number of results per page (max: 100)
        self.variables['page_size'] = self.page_size

        pull_requests = []

        # Fetch data from GitHub, iterate through Pull Requests if there are
        # more pages of data
        while True:
            data = self.send_query(query)
            pull_requests += data['data']['repository']['pullRequests']['nodes']

            # If more pull requests, update cursor to point to new page
            if data['data']['repository']['pullRequests']['pageInfo']['hasNextPage']:
                self.variables['cursor'] = \
                        data['data']['repository']['pullRequests']['pageInfo']['endCursor']
            else:
                # No more data, stop pagination
                break

        # Remove non-default variables
        del self.variables['page_size'], self.variables['cursor']

        return pull_requests

    def post_comments_on_pull_requests(self, comments):
        mutation = \
            """
            mutation($pr_id: ID!, $message: String!){
                addComment(input: {subjectId: $pr_id, body: $message}){
                    subject{
                        id
                    }
                }
            }
            """

        # No need for repository variables in mutation query - store and remove
        # from query variables, to avoid a GitHub error
        repo_name = self.variables['repo_name']
        repo_owner = self.variables['repo_owner']
        del self.variables['repo_owner']
        del self.variables['repo_name']

        # Iterate through stale pull requests, and comment the message chosen
        for c in comments:
            self.variables['pr_id'] = c[0]['id']
            self.variables['message'] = c[1]
            self.send_query(mutation)

        try:
            del self.variables['pr_id']
            del self.variables['message']
        except KeyError:
            pass

        # Restore repository variables
        self.variables['repo_name'] = repo_name
        self.variables['repo_owner'] = repo_owner
