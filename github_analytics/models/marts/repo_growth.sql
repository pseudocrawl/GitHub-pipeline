-- Calculate star growth over time per repo

WITH daily_stars AS(
SELECT repo_name, DATE(scraped_at) AS `date`, stars,
       LAG(stars) OVER (PARTITION BY repo_name ORDER BY (DATE(scraped_at))) AS prev_day_stars
FROM {{ref('stg_github_repos')}}
),

growth AS(
SELECT repo_name, date, stars, prev_day_stars,
       stars - COALESCE(prev_day_stars, stars) AS stars_gained_today,
       ROUND(SAFE_DIVIDE(stars - COALESCE(prev_day_stars, stars), COALESCE(prev_day_stars, stars))
       * 100,2) AS daily_growth_pct
FROM daily_stars
)

SELECT * FROM growth