# Kenneth Kaputula · Data Science

Three independent studies of demand, campaign response, and customer spending. Each includes a concrete question, reproducible analysis, validation results, and limits on interpretation.

**[Explore the portfolio](https://governorkaputula.github.io/data-science-portfolio/)**


## Flagship energy study

**[Zambia Solar Resource Observatory](https://github.com/GovernorKaputula/zambia-solar-resource)** adds an engineering-focused investigation: twelve years of NASA POWER data, six locations, a resource explorer, and a chronological forecast benchmark. [Open the application](https://governorkaputula.github.io/zambia-solar-resource/).

[![Check portfolio](https://github.com/GovernorKaputula/data-science-portfolio/actions/workflows/check.yml/badge.svg)](https://github.com/GovernorKaputula/data-science-portfolio/actions/workflows/check.yml)

## Selected work

| Study | Method | Verified finding | Read |
| --- | --- | --- | --- |
| Hourly bike demand | Chronological holdout, seasonal baseline, gradient boosting | 42.26 holdout MAE; 53.0% lower than the recent seasonal baseline | [Study](reports/demand/case-study.md) · [Code](src/demand.py) |
| Campaign response ranking | Temporal split, leakage-aware features, budget evaluation | 1.95× lift at the top 20%; substantial probability underestimation under distribution shift | [Study](reports/campaign/case-study.md) · [Code](src/campaign.py) |
| Wholesale customer patterns | Log scaling, k-means, bootstrap stability, outlier sensitivity | Two broad groups; median bootstrap ARI 0.937 and silhouette 0.290 | [Study](reports/segments/case-study.md) · [Code](src/segments.py) |

These are measured analytical findings on public data. They are not claims of client revenue, production deployment, or causal business impact.

## Reproduce

Tested with Python 3.12. Install the analysis dependencies in an isolated environment:

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py all
python scripts/sql_audit.py
python -m unittest discover -s tests -v
python build.py
python -m http.server 4173 --directory dist --bind 127.0.0.1
```

Open `http://127.0.0.1:4173`. The build produces a responsive four-page static website and a downloadable source archive. It uses local CSS, JavaScript, and SVG: no analytics, remote fonts, or application keys.

For one study, run `python run.py demand`, `campaign`, or `segments`. Committed result files make the website readable without retraining. `requirements.txt` pins core scientific packages; `requirements-lock.txt` records the packages installed during the verified run. Numerical results can vary slightly across platforms.

## Repository map

```text
src/                Reproducible analysis pipelines
sql/                Independent SQL summaries of row-level outputs
tests/              Checks of published metrics against predictions
reports/            Study notes, metrics, predictions, charts, provenance
website/            Site styles and interactive budget explorer
run.py              Analysis entry point
build.py            Static website generator
dist/               Deployable website
```

## Evaluation decisions

- **Demand:** Select model settings on July–September 2012, evaluate once on October–December. Exclude `casual` and `registered`, which sum to the target. Use observed weather and describe the task accordingly.
- **Campaign:** Exclude call duration and final contact count. Preserve row chronology. Evaluate ranking and calibration separately. Do not equate retrospective lift with incremental conversions.
- **Segmentation:** Exclude channel and region from clustering. Refit preprocessing within each bootstrap. Report overlap as well as stability. Do not label resampling agreement as predictive accuracy.

The tests check demand MAE, campaign budget metrics, and segment profile summaries against row-level outputs. SQL independently checks monthly demand error, ranks campaign deciles, and describes customer channel mix.

## Website and GitHub profile

`dist/` can be served by any static host. Run `python build.py --github-pages` to build into `docs/` for GitHub Pages (main branch, `/docs` folder). GitHub Actions automatically checks saved results, SQL audits, the website build, and local links on pushes and pull requests. The separate manual reproduction workflow reruns the source analyses. `profile-README.md` mirrors the published profile introduction.

## Data attribution

UCI Bike Sharing, Bank Marketing, and Wholesale customers. See [DATA_SOURCES.md](DATA_SOURCES.md) for author citations, source links, licensing, and transformations. Downloaded raw archives stay outside version control.

