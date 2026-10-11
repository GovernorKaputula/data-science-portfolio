-- Channel is used only to describe the fitted spend-based groups.
SELECT segment + 1 AS segment, COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN Channel = 2 THEN 1.0 ELSE 0.0 END), 2) AS retail_pct,
       ROUND(AVG(Fresh + Milk + Grocery + Frozen + Detergents_Paper + Delicassen), 2)
           AS mean_annual_spend
FROM customer_segments
GROUP BY segment
ORDER BY segment;

