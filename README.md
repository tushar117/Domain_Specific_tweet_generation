
## Domain Specific Tweet Generation

This project is part of the course "Information Retrieval and Extraction" from IIIT-H.

In this modern world, a vast amount of news articles are being published online
across domains every day. These articles carry vital information embedded in large
texts, ready to be consumed by the readers. It might be easier for the end-user to
comprehend short rich text snippet to absorb the key information. This can be done
in multiple ways like by posting on micro-blogging sites, social-media or any other
public platforms. Twitter can be used for sharing information to wider audiences, but
generating the specific tweets for each article will be a tedious and time consuming
task.Automated generation of tweets for these articles can contribute for faster
write-up and domain related tweets which can be deployed as an independent
system.

## Requirements

Install required packages using `pip`:
```bash
pip install -r requirement.txt
```

## Performance Analysis

Three different experimental approaches are carried out and following are the
preformance analysis for each of them

### Approach 1 (Pointer Generator network)

| Domains | BLEU (1-gram) | ROUGE (1-gram) |
| --- | --- | --- |
| Entertainment | 0.13 | 0.19 |
| Sports | 0.08 | 0.18 |
| Politics | 0.16 | 0.33 |
| Space-Science | 0.23 | 0.38 |
| Business | 0.20 | 0.31 |


### Approach 2 (SVO based approach)

| Domains | BLEU (1-gram) | ROUGE (1-gram) |
| --- | --- | --- |
| Entertainment | 0.09 | 0.08 |
| Sports | 0.17 | 0.15 |
| Politics | 0.17 | 0.18 |
| Space-Science | 0.06 | 0.07 |
| Business | 0.13 | 0.13 |
| Combined | 0.12 | 0.12 |


### Approach 3 (Topic sentence)
| Domains | Input | Train Model | BLEU (1-gram) | ROUGE (1-gram) |
| --- | --- | --- | --- | --- |
| Entertainment | first sentence | first sentence | 0.49 | 0.50 |
| Sports | first sentence | first sentence | 0.42 | 0.49 |
| Politics | first sentence | first sentence | 0.53 | 0.60 |
| Space-Science | first sentence | first sentence | 0.56 | 0.62 |
| Business | 1 sent. summary | 1 sent. summary | 0.38 | 0.43 |
| Combined | first sentence | first sentence | 0.20 | 0.24 |


## Website
[project site](https://arjungambhir.github.io/Domain_Specific_tweet_generation/)
