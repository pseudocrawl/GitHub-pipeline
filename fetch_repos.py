import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def search_top_repos(query, count=20):
    """Search GitHub for top repos by stars"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q" : query,
        "sort" : "stars",
        "order" : 'desc',
        "per_page" : count
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    repos = []
    for item in data["items"]:
        repos.append(item["full_name"])
    return repos

# Define SaaS categories to search

categories = {
    "data engineering" : "topic:data-engineering stars:>1000 forks:>200",
    "analytics": "topic:analytics stars:>1000 forks:>200",
    "machine learning": "topic:machine-learning stars:>3000 forks:>200",
    "devops":           "topic:devops stars:>1000 forks:>200",
    "developer tools":  "topic:developer-tools stars:>1000 forks:>200",
    "data visualization": "topic:data-visualization stars:>1000 forks:>200",
    "api tools": "topic:api stars:>1000 forks:>200",
    "security": "topic:security stars:>1000 forks:>200",
    "cloud native": "topic:cloud-native stars:>1000 forks:>200",
}

all_repos = []

for category, query in categories.items():
    print(f"Searching category: {category}...")
    repos = search_top_repos(query, count = 20)
    all_repos.extend(repos)
    print(f"Found {len(repos)} repos")

# Remove duplicates

all_repos = list(set(all_repos))
print(f"\nTotal unique repos found: {len(all_repos)}")

# Save to repos.py
with open("repos.py", "w") as f:
    f.write("REPOS = [\n")
    for repo in all_repos:
        f.write(f'   "{repo}",\n')
    f.write("]\n")

print("repos.py created successfully!")
