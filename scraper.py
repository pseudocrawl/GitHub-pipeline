import requests
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from repos import REPOS

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
        "watchers": data["watchers_count"],
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
    """Pull weekly commit count for last 52 weeks"""
    url = f"https://api.github.com/repos/{repo_full_name}/status/commit_activity"
    
    for attempt in range(3): #retry upto 3 times
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 202:
            #GitHub is computing stats, wait and retry
            time.sleep(3)
            continue

        if response.status_code != 200 or not response.json():
            return None

        data = response.json()
        # average commits
        last_4_weeks = data[-4:] if len(data) >= 4 else data
        avg_commits = sum(week["total"] for week in last_4_weeks) / len(last_4_weeks)

        return round(avg_commits,2)

    return None



def scrape_all():
    """Scrape all repos and return as DataFrame"""
    results = []

    for i, repo in enumerate(REPOS):
        print(f"Scraping {i+1}/{len(REPOS)}: {repo}")

        repo_data = get_repo_data(repo)
        if repo_data:
            commit_avg = get_commit_activity(repo)
            repo_data["avg_weekly_commits_4w"] = commit_avg
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