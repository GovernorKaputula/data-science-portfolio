"""Spend-based customer segments with bootstrap stability and sensitivity checks."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from .common import archive, read_member, output_dir, write_json, save_chart, SEED

FEATURES = ["Fresh", "Milk", "Grocery", "Frozen", "Detergents_Paper", "Delicassen"]

def pipeline(k, seed=SEED):
    return make_pipeline(FunctionTransformer(np.log1p), StandardScaler(), KMeans(n_clusters=k, n_init=30, random_state=seed))

def run():
    out = output_dir("segments")
    df = read_member(archive("segments"), "Wholesale customers data.csv")
    assert len(df) == 440 and not df.isna().any().any() and (df[FEATURES] >= 0).all().all()
    X = df[FEATURES]
    candidates, fitted = [], {}
    for k in range(2, 7):
        model = pipeline(k).fit(X)
        z = model[:-1].transform(X)
        labels = model[-1].labels_
        candidates.append({"k": k, "silhouette": float(silhouette_score(z, labels)), "smallest_cluster": int(np.bincount(labels).min())})
        fitted[k] = model
    best = max(candidates, key=lambda r: r["silhouette"])
    k = best["k"]
    model = fitted[k]
    raw_labels = model.predict(X)
    # Make display labels deterministic: descending median Grocery spending.
    order = pd.DataFrame({"cluster": raw_labels, "grocery": X.Grocery}).groupby("cluster").grocery.median().sort_values(ascending=False).index
    mapping = {int(label): i for i, label in enumerate(order)}
    labels = np.array([mapping[int(label)] for label in raw_labels])
    rng = np.random.default_rng(SEED)
    stability = []
    for _ in range(100):
        sampled = X.iloc[rng.integers(0, len(X), len(X))]
        # Refit both scaling and clustering on each sample.
        bootstrap = pipeline(k).fit(sampled)
        stability.append(float(adjusted_rand_score(raw_labels, bootstrap.predict(X))))
    keep = X.sum(axis=1) <= X.sum(axis=1).quantile(.99)
    trimmed = pipeline(k).fit(X[keep])
    sensitivity_ari = float(adjusted_rand_score(raw_labels[keep], trimmed.predict(X[keep])))
    z = model[:-1].transform(X)
    pca = PCA(n_components=2, random_state=SEED).fit(z)
    projection = pca.transform(z)
    medians = X.assign(segment=labels).groupby("segment").median()
    overall = X.median()
    profiles = [{"segment": int(s), "customers": int((labels == s).sum()),
        "medians": {f: float(medians.loc[s, f]) for f in FEATURES},
        "median_ratios": {f: float(medians.loc[s, f] / overall[f]) for f in FEATURES},
        "retail_share": float((df.loc[labels == s, "Channel"] == 2).mean())} for s in range(k)]
    result = {"rows": len(df), "features": FEATURES, "selected_k": k, "candidates": candidates,
        "silhouette": best["silhouette"], "bootstrap_ari_median": float(np.median(stability)),
        "bootstrap_ari_95_interval": np.percentile(stability, [2.5, 97.5]).tolist(),
        "trimmed_top_1_pct_ari": sensitivity_ari, "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
        "profiles": profiles, "projection": [{"x": round(float(p[0]), 3), "y": round(float(p[1]), 3), "segment": int(label)} for p, label in zip(projection, labels)]}
    df.assign(segment=labels).to_csv(out / "customer_segments.csv", index=False)
    write_json(out / "metrics.json", result)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for s in range(k):
        mask = labels == s
        axes[0].scatter(projection[mask, 0], projection[mask, 1], label=f"Segment {s + 1}", alpha=.6, s=20)
    axes[0].set(xlabel="Principal component 1", ylabel="Principal component 2", title="Spend patterns in two dimensions")
    axes[0].legend(frameon=False)
    axes[1].plot([r["k"] for r in candidates], [r["silhouette"] for r in candidates], marker="o")
    axes[1].set(xlabel="Number of clusters", ylabel="Silhouette score", title="Model selection · k = 2 to 6", xticks=range(2, 7))
    save_chart(fig, out / "segment-map.svg")
    return result

