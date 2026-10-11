# Kenneth Gondwe Kaputula

**Electrical & electronics engineering · Data science · Python & SQL**

I investigate practical questions about energy, demand, and customer behavior. My projects pair working code with explicit assumptions, chronological evaluation where appropriate, and results that can be reproduced.

[Portfolio](https://governorkaputula.github.io/data-science-portfolio/) · [Solar resource explorer](https://governorkaputula.github.io/zambia-solar-resource/) · [Email](mailto:kennethkaputula@hotmail.com)

## Selected work

### [Zambia Solar Resource Observatory](https://github.com/GovernorKaputula/zambia-solar-resource)

Twelve years of NASA POWER data across six Zambian locations. An interactive explorer connects seasonal resource patterns with a careful forecast benchmark: delayed inputs, separate model selection and calibration, and an untouched two-year test.

**Finding:** the validation-selected model did not improve on monthly climatology in the final holdout. That result, the weaker candidates, and empirical interval coverage are published alongside the code.

### [Data science studies](https://github.com/GovernorKaputula/data-science-portfolio)

| Question | Evidence |
| --- | --- |
| How well can hourly bike demand be estimated? | 42.26 holdout MAE; 53.0% lower than a recent seasonal baseline, conditional on observed weather. |
| Can campaign contacts be ranked usefully under a response-rate shift? | 1.95× lift at a 20% contact budget; probability underestimation remains a material limitation. |
| Do customer spending groups survive resampling? | Median bootstrap ARI 0.937, with a modest 0.290 silhouette indicating overlap. |

## How I work

- Define the decision and the information available at the time.
- Compare with a credible baseline before adding model complexity.
- Investigate missing data, leakage, uncertainty, and failure cases.
- Publish source attribution, saved outputs, reproducible pipelines, and automated checks.

**Tools used in this work:** Python, pandas, NumPy, scikit-learn, Matplotlib, SQL/SQLite, GitHub Actions, HTML, CSS, and JavaScript.

The repositories contain independent analyses of real public data. Study notes distinguish measured findings from the additional evidence needed for operational use.
