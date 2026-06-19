import requests
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from repos import REPOS
from datetime import datetime, timedelta

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_repo_data(repo_full_name):
    """Pull metadata for a single repo"""
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error fetching {repo_full_name}: {response.status_code}")
        return None

    data = response.json()

    return {
        "repo_name": data["full_name"],
        "description": data.get("description", ""),
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "watchers": data["subscribers_count"],
        "open_issues": data["open_issues_count"],
        "language": data.get("language", ""),
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "pushed_at": data["pushed_at"],
        "size": data["size"],
        "license": data["license"]["name"] if data.get("license") else None,
        "topics": ", ".join(data.get("topics", [])),
        "has_wiki": data["has_wiki"],
        "has_discussions": data.get("has_discussions", False),
        "scraped_at": datetime.now().isoformat(),
    }
    
def get_commit_activity(repo_full_name):
    """Pull total commit count for last 30 days"""
    url = f"https://api.github.com/repos/{repo_full_name}/commits"
    params = {
        "since": (datetime.now() - timedelta(days=30)).isoformat(),
        "per_page": 100
    }

    response = requests.get(url, headers = HEADERS, params = params)
    
    if response.status_code != 200:
        return None
    
    commits = response.json()
    return len(commits)



def scrape_all():
    """Scrape all repos and return as DataFrame"""
    results = []

    for i, repo in enumerate(REPOS):
        print(f"Scraping {i+1}/{len(REPOS)}: {repo}")

        repo_data = get_repo_data(repo)
        if repo_data:
            commit_count = get_commit_activity(repo)
            repo_data["commits_last_30_days"] = commit_count
            results.append(repo_data)

        # 5000 requests/hour allowed
        # Sleep 1 second between calls to not cross the limit
        time.sleep(1)

    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    df = scrape_all()
    if os.path.exists("raw_repo_data.csv"):
        df.to_csv("raw_repo_data.csv", mode='a', header=False, index=False)
    else:
        df.to_csv("raw_repo_data.csv", index=False)
    print(f"Done. Scraped {len(df)} repos.")
    print(df.head())
