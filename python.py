import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

# GitHub username
GITHUB_USERNAME = "mmazinjameel"

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Date of Birth
DOB = datetime(2001, 11, 5)

# SVG file paths
SVG_FILES = ["dark_mode.svg", "light_mode.svg"]

def fetch_github_stats(username):
    try:
        repos_url = f"{GITHUB_API_URL}/users/{username}/repos"
        repos_response = requests.get(repos_url)
        repos_response.raise_for_status()
        repos_data = repos_response.json()

        if not isinstance(repos_data, list):
            print(f"Unexpected response format: {repos_data}")
            return 0, 0, 0

        num_repos = len(repos_data)

        # Approximate number of commits
        num_commits = 0
        for repo in repos_data:
            if not isinstance(repo, dict) or 'name' not in repo:
                print(f"Skipping invalid repo data: {repo}")
                continue

            repo_name = repo['name']
            commits_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/commits"
            commits_response = requests.get(commits_url)
            commits_response.raise_for_status()
            commits_data = commits_response.json()

            if isinstance(commits_data, list):
                num_commits += len(commits_data)

        # Estimate total lines of code (approximation)
        total_loc = 0
        for repo in repos_data:
            if isinstance(repo, dict) and 'size' in repo:
                total_loc += repo['size']  # Size is in KB, not LOC

        return num_repos, num_commits, total_loc

    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub data: {e}")
        return 0, 0, 0

def calculate_uptime(dob):
    now = datetime.now()
    delta = relativedelta(now, dob)
    uptime = f"{delta.years} years, {delta.months} months, {delta.days} days"
    return uptime

def update_svg_file(svg_file, num_repos, num_commits, total_loc, uptime):
    with open(svg_file, 'r', encoding='utf-8') as file:
        svg_content = file.read()

    # Update values
    svg_content = re.sub(r'<tspan class="value" id="repo_data">.*?</tspan>', f'<tspan class="value" id="repo_data">{num_repos}</tspan>', svg_content)
    svg_content = re.sub(r'<tspan class="value" id="commit_data">.*?</tspan>', f'<tspan class="value" id="commit_data">{num_commits}</tspan>', svg_content)
    svg_content = re.sub(r'<tspan class="value" id="loc_data">.*?</tspan>', f'<tspan class="value" id="loc_data">{total_loc}</tspan>', svg_content)
    svg_content = re.sub(r'<tspan class="value" id="age_data">.*?</tspan>', f'<tspan class="value" id="age_data">{uptime}</tspan>', svg_content)

    with open(svg_file, 'w', encoding='utf-8') as file:
        file.write(svg_content)

def main():
    num_repos, num_commits, total_loc = fetch_github_stats(GITHUB_USERNAME)
    uptime = calculate_uptime(DOB)

    for svg in SVG_FILES:
        update_svg_file(svg, num_repos, num_commits, total_loc, uptime)

    print("SVG files updated successfully!")

if __name__ == "__main__":
    main()
