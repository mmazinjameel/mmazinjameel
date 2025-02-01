import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import time
import subprocess

# GitHub username
GITHUB_USERNAME = "mmazinjameel"

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Date of Birth
DOB = datetime(2001, 11, 5)

# SVG file paths
SVG_FILES = ["dark_mode.svg", "light_mode.svg"]

# README file path
README_FILE = "README.md"

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
        num_commits = 0
        total_loc = 0

        for repo in repos_data:
            if not isinstance(repo, dict) or 'name' not in repo:
                print(f"Skipping invalid repo data: {repo}")
                continue

            repo_name = repo['name']

            # Fetch number of commits
            commits_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/commits"
            commits_response = requests.get(commits_url)
            if commits_response.status_code == 200:
                commits_data = commits_response.json()
                if isinstance(commits_data, list):
                    num_commits += len(commits_data)

            # Fetch total lines of code using /languages API (accurate count)
            languages_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/languages"
            languages_response = requests.get(languages_url)
            if languages_response.status_code == 200:
                languages_data = languages_response.json()
                total_loc += sum(languages_data.values())  # Sum of all lines of code

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

    # Update values in the SVG file
    svg_content = re.sub(r'<tspan class="value" id="repo_data">.*?</tspan>', f'<tspan class="value" id="repo_data">{num_repos}</tspan>', svg_content)
    svg_content = re.sub(r'<tspan class="value" id="commit_data">.*?</tspan>', f'<tspan class="value" id="commit_data">{num_commits}</tspan>', svg_content)
    svg_content = re.sub(r'<tspan class="value" id="loc_data">.*?</tspan>', f'<tspan class="value" id="loc_data">{total_loc}</tspan>', svg_content)
    svg_content = re.sub(r'<tspan class="value" id="age_data">.*?</tspan>', f'<tspan class="value" id="age_data">{uptime}</tspan>', svg_content)

    with open(svg_file, 'w', encoding='utf-8') as file:
        file.write(svg_content)

def update_readme():
    """Automatically updates README.md to force fresh SVG load"""
    timestamp = int(time.time())  # Get current timestamp

    with open(README_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    # Replace old timestamp with the new one
    content = re.sub(r"(\?v=)[0-9]+", f"?v={timestamp}", content)

    with open(README_FILE, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"README.md updated with timestamp {timestamp}")

def main():
    num_repos, num_commits, total_loc = fetch_github_stats(GITHUB_USERNAME)
    uptime = calculate_uptime(DOB)

    for svg in SVG_FILES:
        update_svg_file(svg, num_repos, num_commits, total_loc, uptime)

    update_readme()

    print("SVG files and README.md updated successfully!")

if __name__ == "__main__":
    main()
