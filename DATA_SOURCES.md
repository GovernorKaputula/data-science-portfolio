# Data sources and provenance

All three studies use real, public datasets from the UCI Machine Learning Repository. They are independent analytical projects, not client engagements. The analyses transform the original data; they do not claim to have collected it.

| Study | Dataset and attribution | Source |
| --- | --- | --- |
| Hourly demand | Fanaee-T, H. (2013). Bike Sharing. Capital Bikeshare rental counts from 2011–2012. | [UCI / DOI](https://doi.org/10.24432/C5W894) |
| Campaign response | Moro, S., Rita, P., & Cortez, P. (2014). Bank Marketing. Uses the full, date-ordered 41,188-row additional file. | [UCI / DOI](https://doi.org/10.24432/C5K306) |
| Customer segmentation | Cardoso, M. (2013). Wholesale customers. Annual category spending for 440 customers. | [UCI / DOI](https://doi.org/10.24432/C5030X) |

UCI lists these datasets under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). This attribution applies to the original datasets and derived data tables. The dataset license does not imply endorsement by the authors or UCI.

`reports/provenance.json` contains the exact archive URLs and SHA-256 checksums from the run. The original ZIP files are downloaded to ignored `data/raw/` storage. No API credentials are needed.

The hourly bike CSV contains **17,379** rows; this is the count used in the analysis, rather than the differing count displayed in UCI's catalog summary. The bank data retains original row order, including repeated records, because duplicate-looking records cannot safely be assumed to represent duplicate events without customer identifiers. The wholesale monetary unit is unspecified; figures are not labeled as dollars.

Transforms: bike records are sorted and split by date; campaign variables are explicitly restricted and the never-contacted sentinel is encoded; wholesale spend is log-transformed and standardized. All original authors retain credit for their datasets.

