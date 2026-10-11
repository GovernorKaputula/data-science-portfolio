"""Independent checks of published claims against the saved row-level outputs."""
from pathlib import Path
import json
import math
import unittest
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

class PublishedResultsTest(unittest.TestCase):
    def metrics(self, study):
        return json.loads((ROOT / "reports" / study / "metrics.json").read_text())

    def test_demand_holdout_and_published_errors(self):
        frame = pd.read_csv(ROOT / "reports/demand/holdout_predictions.csv")
        metrics = self.metrics("demand")
        self.assertEqual(len(frame), metrics["test_rows"])
        self.assertEqual(frame.dteday.min(), "2012-10-01")
        self.assertEqual(frame.dteday.max(), "2012-12-31")
        self.assertFalse(frame.duplicated(["dteday", "hr"]).any())
        self.assertTrue((frame.prediction >= 0).all())
        model_error = np.mean(np.abs(frame.cnt - frame.prediction))
        baseline_error = np.mean(np.abs(frame.cnt - frame.baseline))
        self.assertAlmostEqual(model_error, metrics["test"]["mae"], places=8)
        self.assertAlmostEqual(100*(1-model_error/baseline_error), metrics["mae_reduction_pct"], places=8)

    def test_campaign_budget_claims_and_ties(self):
        frame = pd.read_csv(ROOT / "reports/campaign/holdout_predictions.csv")
        metrics = self.metrics("campaign")
        self.assertEqual(len(frame), metrics["test_rows"])
        self.assertTrue(frame.source_row.is_monotonic_increasing)
        self.assertTrue(frame.score.between(0, 1).all())
        ranked = frame.sort_values(["score", "source_row"], ascending=[False, True])
        for claim in metrics["budgets"]:
            n = math.ceil(len(frame)*claim["budget_pct"]/100)
            selected = ranked.iloc[:n]
            self.assertEqual(n, claim["contacts"])
            self.assertEqual(int(selected.response.sum()), claim["responses"])
            self.assertAlmostEqual(selected.response.mean()/frame.response.mean(), claim["lift"], places=10)
        brier = np.mean((frame.response-frame.score)**2)
        self.assertAlmostEqual(brier, metrics["test"]["brier"], places=10)

    def test_segment_profiles_match_customers(self):
        frame = pd.read_csv(ROOT / "reports/segments/customer_segments.csv")
        metrics = self.metrics("segments")
        self.assertEqual(len(frame), metrics["rows"])
        self.assertEqual(frame.segment.nunique(), metrics["selected_k"])
        for profile in metrics["profiles"]:
            group = frame[frame.segment == profile["segment"]]
            self.assertEqual(len(group), profile["customers"])
            for column in metrics["features"]:
                self.assertAlmostEqual(group[column].median(), profile["medians"][column])
        self.assertGreaterEqual(metrics["bootstrap_ari_median"], -1)
        self.assertLessEqual(metrics["bootstrap_ari_median"], 1)

    def test_sql_independently_reproduces_monthly_mae(self):
        frame = pd.read_csv(ROOT / "reports/sql/demand_by_month.csv")
        metrics = self.metrics("demand")
        self.assertEqual(len(frame), 3)
        for row, expected in zip(frame.itertuples(), metrics["monthly"]):
            self.assertEqual(row.month, expected["month"])
            self.assertAlmostEqual(row.model_mae, expected["mae"], places=3)

if __name__ == "__main__":
    unittest.main()

