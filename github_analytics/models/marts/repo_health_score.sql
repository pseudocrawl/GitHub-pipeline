-- Health Score

SELECT repo_name, `language`, stars, forks, open_issues, commits_last_30_days,
        DATE(scraped_at) AS date,
        ROUND((LEAST(stars/10000.0, 1.0) * 30)
        + (LEAST(forks/1000.0,1.0) * 20)
        + (LEAST(commits_last_30_days/50, 1.0)* 40)
        + CASE WHEN open_issues < 100 THEN 1.0
               WHEN open_issues < 50 THEN 0.5 
               ELSE 0.2 END * 10 ,0)
        AS health_score

FROM {{ref('stg_github_repos')}}