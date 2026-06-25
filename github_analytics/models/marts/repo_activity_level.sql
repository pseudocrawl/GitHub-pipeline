SELECT CASE WHEN commits_last_30_days >=50 THEN 'high_activity'
            WHEN commits_last_30_days >=30 THEN 'medium_activity'
            ELSE 'low_activity'
            END AS activity_level,
       COUNT(*) AS repo_count,
       ROUND(AVG(health_score),2) AS avg_health,
       ROUND(AVG(stars),2) AS avg_stars
FROM `project-574b3547-7112-4651-817.github_analytics.repo_health_score_latest` 
GROUP BY activity_level
ORDER BY avg_health DESC
