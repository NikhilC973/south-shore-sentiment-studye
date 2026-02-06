# Limitations — South Shore Sentiment Study

## Selection Bias
Data is limited to public posts on Reddit and news sites. Affected community members — particularly undocumented residents, non-English speakers, and those without reliable internet access — may not use these platforms. The dataset overrepresents English-speaking, digitally-connected individuals and likely underrepresents the most directly affected populations.

## Platform Bias
Reddit skews younger, more male, and more tech-savvy than the general population. News comment sections tend to attract more politically engaged users. Neither platform is representative of South Shore's demographics (predominantly Black, with a significant immigrant population).

## Geo-Inference Error
Neighborhood assignment is based entirely on text mention matching (e.g., a post containing "South Shore" is tagged as referencing that neighborhood). This does not confirm the poster's location. People commenting on the raid from other parts of Chicago or the country are tagged if they mention South Shore. True geographic analysis would require verified location data, which we do not collect.

## Model Uncertainty
- **VADER** is lexicon-based and may miss sarcasm, code-switching, and AAVE (African-American Vernacular English) patterns common in Chicago discourse.
- **RoBERTa** was fine-tuned on general social media and may not capture community-specific language patterns.
- **GoEmotions** was trained on Reddit data; generalization to news comments may be imperfect. Emotion probability thresholds (0.3 minimum) were applied but are somewhat arbitrary.
- **BERTopic** results depend on embedding model choice and HDBSCAN parameters; different configurations may produce different topic clusters.

## Temporal Resolution
The event window is defined as ±24 hours around September 30. Finer temporal resolution (hourly) would be valuable but is limited by post volume and timestamp precision.

## Synthetic Data
When live data collection yields insufficient volume, synthetic data supplements the analysis. Synthetic posts follow expected discourse patterns but cannot capture authentic community voice. Analysis results based partially on synthetic data should be interpreted as illustrative, not definitive.

## Causal Claims
This study measures correlation between the raid event and shifts in public discourse. It does not establish causation. External factors (media coverage cycles, other news events, seasonal patterns) may contribute to observed sentiment changes.
