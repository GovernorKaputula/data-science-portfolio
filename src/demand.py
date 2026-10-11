"""Conditional bike demand estimation with a strictly chronological holdout."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .common import archive, read_member, output_dir, write_json, save_chart, SEED

FEATURES = ["season", "yr", "mnth", "hr", "holiday", "weekday", "workingday", "weathersit", "temp", "atemp", "hum", "windspeed"]
CATEGORICAL = FEATURES[:8]

def regression_metrics(y, prediction):
    return {"mae": float(mean_absolute_error(y, prediction)),
        "rmse": float(np.sqrt(mean_squared_error(y, prediction))), "r2": float(r2_score(y, prediction))}

def seasonal_prediction(history, future):
    # A recent baseline adapts to the increase in ridership between years.
    recent = history[history.dteday >= history.dteday.max() - pd.Timedelta(days=89)]
    means = recent.groupby(["weekday", "hr"])["cnt"].mean()
    fallback = recent.groupby("hr")["cnt"].mean()
    return np.array([means.get((r.weekday, r.hr), fallback.get(r.hr, recent.cnt.mean())) for r in future.itertuples()])

def run():
    out = output_dir("demand")
    df = read_member(archive("bike"), "hour.csv", parse_dates=["dteday"]).sort_values(["dteday", "hr"]).reset_index(drop=True)
    assert len(df) == 17379 and not df.isna().any().any()
    assert not df.duplicated(["dteday", "hr"]).any()
    assert (df.cnt == df.casual + df.registered).all()
    assert not {"cnt", "casual", "registered", "instant"}.intersection(FEATURES)
    train = df[df.dteday < "2012-07-01"]
    valid = df[(df.dteday >= "2012-07-01") & (df.dteday < "2012-10-01")]
    test = df[df.dteday >= "2012-10-01"]
    assert train.dteday.max() < valid.dteday.min() < test.dteday.min()
    prep = ColumnTransformer([("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ("numeric", StandardScaler(), FEATURES[8:])])
    candidates = {"ridge": make_pipeline(prep, Ridge(alpha=10))}
    for leaves in [15, 31, 63]:
        candidates[f"boosting_{leaves}"] = HistGradientBoostingRegressor(max_leaf_nodes=leaves, max_iter=200,
            learning_rate=.08, min_samples_leaf=30, l2_regularization=1, early_stopping=False, random_state=SEED)
    validation = {"seasonal_baseline": regression_metrics(valid.cnt, seasonal_prediction(train, valid))}
    for name, model in candidates.items():
        model.fit(train[FEATURES], train.cnt)
        validation[name] = regression_metrics(valid.cnt, np.maximum(0, model.predict(valid[FEATURES])))
    winner = min(validation, key=lambda name: validation[name]["mae"])
    fit = pd.concat([train, valid])
    baseline = seasonal_prediction(fit, test)
    if winner == "seasonal_baseline":
        prediction = baseline
    else:
        selected = candidates[winner].fit(fit[FEATURES], fit.cnt)
        prediction = np.maximum(0, selected.predict(test[FEATURES]))
    scored = test[["dteday", "hr", "cnt"]].copy()
    scored["prediction"] = prediction
    scored["baseline"] = baseline
    scored["absolute_error"] = np.abs(scored.cnt - prediction)
    scored["baseline_error"] = np.abs(scored.cnt - baseline)
    daily_errors = scored.groupby("dteday")[["absolute_error", "baseline_error"]].sum().values
    rng = np.random.default_rng(SEED)
    resampled = daily_errors[rng.integers(0, len(daily_errors), (2000, len(daily_errors)))].sum(axis=1)
    reduction = 1 - resampled[:, 0] / resampled[:, 1]
    intervals = np.percentile(reduction, [2.5, 97.5]) * 100
    model_metrics, baseline_metrics = regression_metrics(test.cnt, prediction), regression_metrics(test.cnt, baseline)
    monthly = scored.assign(month=scored.dteday.dt.strftime("%Y-%m")).groupby("month").agg(mae=("absolute_error", "mean"), baseline_mae=("baseline_error", "mean"), hours=("cnt", "size")).reset_index()
    profile = scored.groupby("hr")[["cnt", "prediction", "baseline"]].mean().reset_index()
    daily = scored.groupby("dteday")[["cnt", "prediction", "baseline"]].sum().reset_index()
    result = {"rows": len(df), "train_rows": len(train), "validation_rows": len(valid), "test_rows": len(test),
        "selected_model": winner, "features": FEATURES, "validation": validation, "test": model_metrics,
        "baseline": baseline_metrics, "mae_reduction_pct": float(100 * (1 - model_metrics["mae"] / baseline_metrics["mae"])),
        "reduction_bootstrap_95_pct": intervals.tolist(), "bootstrap_unit": "observed calendar day; 2000 paired resamples",
        "test_start": str(test.dteday.min().date()), "test_end": str(test.dteday.max().date()),
        "monthly": monthly.to_dict(orient="records"), "hourly_profile": profile.round(2).to_dict(orient="records"),
        "daily_totals": [{"date": str(r.dteday.date()), "actual": int(r.cnt), "prediction": round(r.prediction), "baseline": round(r.baseline)} for r in daily.itertuples()]}
    scored.to_csv(out / "holdout_predictions.csv", index=False)
    write_json(out / "metrics.json", result)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(profile.hr, profile.cnt, label="Observed", lw=2.5)
    ax.plot(profile.hr, profile.prediction, label="Selected model", lw=2, linestyle="--")
    ax.plot(profile.hr, profile.baseline, label="Seasonal baseline", lw=1.5, alpha=.7)
    ax.set(xlabel="Hour of day", ylabel="Mean hourly rentals", title="Demand through the day · October–December 2012")
    ax.legend(frameon=False)
    save_chart(fig, out / "hourly-profile.svg")
    return result

