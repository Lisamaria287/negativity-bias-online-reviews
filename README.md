# Negativity Bias in Online Reviews

Independent research project testing whether negative restaurant reviews are rated as more useful than positive ones, using 50,000 reviews from the Yelp Open Dataset.

**Main finding:** Negative reviews received slightly more "useful" votes, but this was largely explained by length. Review length was by far the strongest predictor of usefulness.

- Preregistration: https://doi.org/10.17605/OSF.IO/K9PMN
- Report: see the PDF in this repository
- Code: `yelp_sample.py` (sampling) and `review_analysis.ipynb` (analysis in Python: pandas, SciPy, statsmodels)

The Yelp data are not included, in line with Yelp's terms of use. Download them from https://www.yelp.com/dataset and run `yelp_sample.py` to recreate the sample.

Author: Lisa Cretan, Erasmus University Rotterdam
