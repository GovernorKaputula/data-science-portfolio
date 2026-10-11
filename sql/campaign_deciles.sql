-- Fixed-size ranking buckets; source order makes ties deterministic.
WITH ranked AS (
    SELECT response, score,
           NTILE(10) OVER (ORDER BY score DESC, source_row ASC) AS decile
    FROM campaign_predictions
), base AS (
    SELECT AVG(response * 1.0) AS response_rate FROM campaign_predictions
)
SELECT decile, COUNT(*) AS contacts, SUM(response) AS responses,
       ROUND(AVG(response * 1.0), 4) AS precision,
       ROUND(AVG(response * 1.0) / NULLIF(base.response_rate, 0), 4) AS lift
FROM ranked CROSS JOIN base
GROUP BY decile, base.response_rate
ORDER BY decile;

