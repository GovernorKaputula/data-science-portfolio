"""Campaign response ranking without information from the completed call."""
from io import BytesIO
import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.calibration import calibration_curve
from .common import archive, read_member, output_dir, write_json, save_chart, SEED

FEATURES = ["contact", "month", "day_of_week", "pdays", "previous", "poutcome", "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
CATS = ["contact", "month", "day_of_week", "poutcome"]

def response_metrics(y, scores):
    return {"average_precision": float(average_precision_score(y, scores)), "roc_auc": float(roc_auc_score(y, scores)),
        "brier": float(brier_score_loss(y, scores))}

def ranked_budget(y, scores, share):
    n = max(1, int(np.ceil(len(y) * share)))
    indices = np.argsort(-np.asarray(scores), kind="stable")[:n]
    positives = int(np.asarray(y)[indices].sum())
    precision = positives / n
    return {"budget_pct": round(share * 100), "contacts": n, "responses": positives,
        "precision": precision, "recall": positives / int(np.sum(y)), "lift": precision / float(np.mean(y))}

def run():
    out = output_dir("campaign")
    outer = archive("campaign")
    nested = zipfile.ZipFile(BytesIO(outer.read("bank-additional.zip")))
    df = read_member(nested, "bank-additional-full.csv", sep=";")
    assert len(df) == 41188 and set(df.y) == {"yes", "no"}
    assert "duration" not in FEATURES and "campaign" not in FEATURES
    assert not df[FEATURES].isna().any().any()
    # 999 is 'never contacted', not a literal elapsed period.
    df["previously_contacted"] = (df.pdays != 999).astype(int)
    df["pdays"] = df.pdays.replace(999, 0)
    features = FEATURES + ["previously_contacted"]
    a, b = int(.6 * len(df)), int(.8 * len(df))
    train, valid, test = df.iloc[:a], df.iloc[a:b], df.iloc[b:]
    target = lambda frame: (frame.y == "yes").astype(int)
    preprocess = lambda: ColumnTransformer([("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATS),
        ("numeric", StandardScaler(), [x for x in features if x not in CATS])])
    candidates = {"logistic": make_pipeline(preprocess(), LogisticRegression(C=1, max_iter=2000, random_state=SEED))}
    for leaves in [7, 15]:
        candidates[f"boosting_{leaves}"] = make_pipeline(preprocess(), HistGradientBoostingClassifier(max_leaf_nodes=leaves,
            max_iter=150, learning_rate=.05, min_samples_leaf=80, l2_regularization=5, early_stopping=False, random_state=SEED))
    validation = {}
    for name, model in candidates.items():
        model.fit(train[features], target(train))
        validation[name] = response_metrics(target(valid), model.predict_proba(valid[features])[:, 1])
    winner = max(validation, key=lambda name: validation[name]["average_precision"])
    fit = df.iloc[:b]
    model = candidates[winner].fit(fit[features], target(fit))
    y = target(test).to_numpy()
    scores = model.predict_proba(test[features])[:, 1]
    budgets = [ranked_budget(y, scores, p / 100) for p in [5, 10, 20, 30, 40, 50, 75, 100]]
    observed, predicted = calibration_curve(y, scores, n_bins=8, strategy="quantile")
    result = {"rows": len(df), "train_rows": len(train), "validation_rows": len(valid), "test_rows": len(test),
        "selected_model": winner, "features": features, "validation": validation, "test": response_metrics(y, scores),
        "train_prevalence": float(target(train).mean()), "validation_prevalence": float(target(valid).mean()),
        "fit_prevalence": float(target(fit).mean()), "test_prevalence": float(y.mean()),
        "constant_baseline_brier": float(brier_score_loss(y, np.full(len(y), target(fit).mean()))),
        "top_20": budgets[2], "budgets": budgets,
        "calibration": [{"predicted": float(p), "observed": float(o)} for p, o in zip(predicted, observed)]}
    pd.DataFrame({"source_row": test.index + 1, "response": y, "score": scores}).to_csv(out / "holdout_predictions.csv", index=False)
    write_json(out / "metrics.json", result)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot([0] + [r["budget_pct"] for r in budgets], [0] + [r["recall"] * 100 for r in budgets], marker="o", lw=2.5, label="Model ranking")
    ax.plot([0, 100], [0, 100], linestyle="--", label="Random targeting", color="#879b91")
    ax.set(xlabel="Share of holdout contacts selected (%)", ylabel="Share of observed responses captured (%)", title="Campaign prioritisation · chronological holdout", xlim=(0, 100), ylim=(0, 100))
    ax.legend(frameon=False)
    save_chart(fig, out / "gains-curve.svg")
    return result

