-- Staging model: clean raw data, rename columns, cast types

{{ config(materialized='view') }}

SELECT 
    repo_name,
    `description`,
    CAST(stars AS INT64) AS stars,
    CAST(forks AS INT64) AS forks,
    CAST(open_issues AS INT64) AS open_issues,
    `language`,
    TIMESTAMP(created_at) AS created_at,
    TIMESTAMP(updated_at) AS updated_at,
    scraped_at,
    commits_last_30_days,
    topics,
    license

FROM {{source('raw', 'github_repos')}}
WHERE repo_name IS NOT NULL