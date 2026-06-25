--Latest health score

WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY repo_name ORDER BY `date` DESC) AS rn
    FROM {{ref('repo_health_score')}}
)

SELECT * EXCEPT(rn)
FROM ranked
WHERE rn =1