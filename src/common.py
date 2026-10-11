"""Data provenance, deterministic output, and shared chart styling."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import urllib.request
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "reports"
SEED = 42
SOURCES = {
    "bike": ("https://archive.ics.uci.edu/static/public/275/bike%2Bsharing%2Bdataset.zip", "https://doi.org/10.24432/C5W894"),
    "campaign": ("https://archive.ics.uci.edu/static/public/222/bank%2Bmarketing.zip", "https://doi.org/10.24432/C5K306"),
    "segments": ("https://archive.ics.uci.edu/static/public/292/wholesale%2Bcustomers.zip", "https://doi.org/10.24432/C5030X"),
}

def archive(name):
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"{name}.zip"
    if not path.exists():
        request = urllib.request.Request(SOURCES[name][0], headers={"User-Agent": "PortfolioResearch/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        zipfile.ZipFile(BytesIO(data)).testzip()
        path.write_bytes(data)
    return zipfile.ZipFile(path)

def read_member(z, suffix, **kwargs):
    matches = [n for n in z.namelist() if n.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one {suffix}: {matches}")
    return pd.read_csv(BytesIO(z.read(matches[0])), **kwargs)

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def output_dir(name):
    path = OUT / name
    path.mkdir(parents=True, exist_ok=True)
    return path

def style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.edgecolor": "#b9c3bd", "axes.labelcolor": "#384b43",
        "text.color": "#193c30", "xtick.color": "#5d7168", "ytick.color": "#5d7168",
        "figure.facecolor": "#f7f6f0", "axes.facecolor": "#f7f6f0", "savefig.facecolor": "#f7f6f0",
        "axes.prop_cycle": plt.cycler(color=["#23654b", "#bc6840", "#8c9e48", "#63938b", "#886d89"]),
        "svg.fonttype": "none"})

def save_chart(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

def provenance():
    result = {}
    for name, (url, doi) in SOURCES.items():
        path = RAW / f"{name}.zip"
        result[name] = {"download_url": url, "doi": doi, "license": "CC BY 4.0",
            "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    write_json(OUT / "provenance.json", result)

