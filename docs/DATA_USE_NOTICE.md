# Data Use and Attribution Notice

## Selected source

The project is designed around the Financial Data Set from the PKDD'99 Discovery Challenge, prepared by Petr Berka and Marta Sochorova from anonymized Czech bank data.

Source page: <https://sorry.vse.cz/~berka/challenge/pkdd1999/berka.htm>

Source archive: <https://sorry.vse.cz/~berka/challenge/pkdd1999/data_berka.zip>

## License caveat

The dataset was publicly distributed for the discovery challenge, but this project has not found an explicit modern license that grants redistribution. Public availability is not treated as equivalent to an open-data license.

Therefore:

- raw source files and the downloaded archive are not committed to Git;
- the project does not relicense or redistribute the source data;
- users deliberately acknowledge this caveat before the download script runs;
- attribution and source links remain in the public documentation;
- charts and aggregate results will be presented as analysis of the source, with no personal data claims.

This is a conservative repository policy, not legal advice. If an employer, school, or hosting platform requires an explicit data license, use the CC BY 4.0 UCI fallback documented in `DATASET_EVALUATION.md`.

## Test data

Any future files under `tests/fixtures/` will be tiny, newly created synthetic records for automated tests. They must not be excerpts copied from the original dataset and must be labelled synthetic.
