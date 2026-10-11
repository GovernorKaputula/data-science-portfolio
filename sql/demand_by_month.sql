-- Score the saved holdout predictions independently of the Python metrics.
SELECT substr(dteday, 1, 7) AS month,
       COUNT(*) AS observed_hours,
       ROUND(AVG(ABS(cnt - prediction)), 4) AS model_mae,
       ROUND(AVG(ABS(cnt - baseline)), 4) AS baseline_mae,
       ROUND(100.0 * (1.0 - SUM(ABS(cnt - prediction)) /
           NULLIF(SUM(ABS(cnt - baseline)), 0)), 2) AS mae_reduction_pct
FROM demand_predictions
GROUP BY substr(dteday, 1, 7)
ORDER BY month;

