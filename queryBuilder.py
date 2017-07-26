import json
import requests
from datetime import datetime

# Class for handling GraphQL queries for GitHub's APIv4
class Query(object):
    # Initialise default parameters
    def __init__(self):
        # GitHub APIv4 endpoint
        self.endpoint = "https://api.github.com/graphql"

        # Create GraphQL Authorization header
        # Fetch GitHub Personal Authentication Token
        pat_file = open('personal_access_token.txt', 'r')
        bearer_token = "Bearer %s" % pat_file.readline().replace('\n', '')
        pat_file.close()
        # Insert into header
        self.auth = {"Authorization": bearer_token}

        # Initialise empty GraphQL variables dictionary
        self.variables = {'repo_owner': 'mantidproject', 'repo_name' : 'mantid'}

        # Threshold for pull requests to become stale (days)
        self.staleThreshold = 7
        # Number of results to return per page
        self.page_size = 25

    # Sends Query as JSON object, reply formatted as nested python dictionary
    def sendQuery(self, query):
        # Read query and variables into JSON formatted string
        message = json.dumps({"query": query, "variables": self.variables})
        # Convert Python None to JSON null
        payload = message.replace("None", "null")

        # Post Query, recieve reply
        reply = requests.post(self.endpoint, payload, headers=self.auth)

        # Return reply as a nested Python dictionary
        return reply.json()

    # Calculates the difference between time now and the input time in days
    def elapsedDays(self, timeString):
        inputTime = datetime.strptime(timeString, "%Y-%m-%dT%H:%M:%SZ")

        return (datetime.now() - inputTime).days


    # Fetches pull request number of all stale pull requests
    def fetchStalePullRequests(self):
        # GraphQL query
        query = """
query($repo_owner: String!, $repo_name: String!, $page_size: Int!, $cursor: String){
    repository(owner: $repo_owner, name: $repo_name){
        pullRequests(first: $page_size, after: $cursor, states: [OPEN]){
            pageInfo{
                hasNextPage
                endCursor
            }
            nodes{
                number
                updatedAt
            }
        }
    }
}
"""
        # Create optional cursor variable (used for pagination)
        self.variables['cursor'] = None
        # Set number of results per page (max: 100)
        self.variables['page_size'] = self.page_size

        # Container for Pull Request: number, updatedAt fields
        stalePRs = []

        # Fetch data from GitHub, iterate through Pull Requests if
        # there are more pages of data
        while True:
            #Store reply
            data = self.sendQuery(query)

            # Iterate through the nodes list, check if Pull Request is stale
            # If stale, append PR to list of stale Pull Requests
            for pullRequest in data['data']['repository']['pullRequests']['nodes']:
                # Check if pull request is stale
                days_dormant = self.elapsedDays(pullRequest['updatedAt'])

                if days_dormant >= self.staleThreshold:
                    stalePRs.append([pullRequest['number'], days_dormant])

            # If more pull requests, update cursor to point to new page
            if data['data']['repository']['pullRequests']['pageInfo']['hasNextPage']:
                self.variables['cursor'] = data['data']['repository']['pullRequests']\
                                           ['pageInfo']['endCursor']
            else:
                # No more data, stop pagination
                break

        # Remove non-default variables
        del self.variables['page_size'], self.variables['cursor']

        # Return stale Pull Requests as tuple (number, days elapsed)
        return stalePRs


    # Fetches the status and author of the most recent commits on each pull request
    def sortPRs_buildStatus(self, PRlist):
        # Graph QL query
        query = """
query($repo_owner: String!, $repo_name: String!, $pr_number: Int!){
    repository(owner: $repo_owner, name: $repo_name){
        pullRequest(number: $pr_number){
            commits(last: 1){
                nodes{
                    commit{
                        author{
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
        }
    }
}
"""
        successful_commits = []
        failed_commits = []
        for PR in PRlist:
            self.variables['pr_number'] = PR[0]
            data = self.sendQuery(query)

            commit_status = data['data']['repository']['pullRequest']['commits']\
                                ['nodes'][0]['commit']['status']['state']
            # Catch if user = None (potentially because account has been removed from mantid team)
            try:
                commit_author = data['data']['repository']['pullRequest']\
                                    ['commits']['nodes'][0]['commit']['author']\
                                    ['user']['login']
            except TypeError:
                commit_author = ''

            PR.append(commit_author)
            if commit_status == 'SUCCESS':
                successful_commits.append(PR)
            else:
                failed_commits.append(PR)

        # Clear up variables
        try:
            del self.variables['pr_number']
        except KeyError:
            print('No stale Pull Requests')

        return (successful_commits, failed_commits)


    # Checks for any reviews/assignees
    def fetchReviews(self, PRlist):
        query = """
query($repo_owner: String!, $repo_name: String!, $pr_number: Int!){
    repository(owner: $repo_owner, name: $repo_name){
        pullRequest(number: $pr_number){
            reviews(last: 1){
                nodes{
                    author{
                        login
                    }
                    state
                }
            }
            reviewRequests(last: 1){
                nodes{
                    reviewer{
                        login
                    }
                }
            }
            assignees(last: 10){
                nodes{
                    login
                }
            }
            mergeable
        }
    }
}
"""
        # Loop through PRs which have built successfully
        for PR in PRlist:
            # Set pr_number variable
            self.variables['pr_number'] = PR[0]
            # Send Query
            data = self.sendQuery(query)

            # Store data variables
            try:
                review = data['data']['repository']['pullRequest']['reviews']\
                            ['nodes'][0]
                try:
                    review_author = review['author']['login']
                except TypeError:
                    review_author = None
                review_state = review['state']
            except IndexError:
                review_author = None
                review_state = None

            try:
                request = data['data']['repository']['pullRequest']\
                            ['reviewRequests']['nodes'][0]
                try:
                    reviewer = request['reviewer']['login']
                except TypeError:
                    reviewer = None
            except IndexError:
                reviewer = None

            # Assignees
            assignees = []
            try:
                for assignee in data['data']['repository']['pullRequest']\
                                ['assignees']['nodes']:
                    assignees.append(assignee['login'])
            except TypeError:
                assignees = None

            mergeable = data['data']['repository']['pullRequest']['mergeable']

            print(PR[0], PR[1], review_author, review_state, reviewer, assignees,
                    mergeable)


# Testing
if __name__ == '__main__':
    g = Query()
    PRlist = g.fetchStalePullRequests()
    successes, fails = g.sortPRs_buildStatus(PRlist)
    g.fetchReviews(successes)
