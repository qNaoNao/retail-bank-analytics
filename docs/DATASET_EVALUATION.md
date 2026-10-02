# Dataset Evaluation

Reviewed on 2026-09-29. The goal is not merely to find a banking-labelled CSV; it is to support a credible relational analytics product.

| Candidate | Reality / shape | Access and terms | What it supports well | Main limitation | Decision |
|---|---|---|---|---|---|
| **Berka / PKDD'99 Czech Financial Dataset** | Real anonymized bank data; 8 tables; 5,369 clients; 4,500 accounts; 1,056,320 transactions; loans, cards, orders, and district data | Current public academic database plus pinned file mirror; explicit modern license not found | Multi-table SQL, customer 360, transaction behaviour, account activity cohort, product adoption, lending risk | Historical data; licensing/redistribution caveat | **Primary** |
| **UCI Bank Marketing** | Real Portuguese bank campaign data; 45,211 rows; essentially a flat campaign modelling table | Direct download, about 1 MB; CC BY 4.0 | Funnel/campaign conversion, interpretable classification, leakage discussion around call duration | No account/transaction model, weak customer 360, common portfolio topic | Fallback if explicit licensing is mandatory |
| **UCI Default of Credit Card Clients** | 30,000 Taiwan credit-card clients with six months of bill/payment fields; flat table | Direct 5.3 MB download; CC BY 4.0 | Credit-risk classification and temporal repayment features | No relational joins, cohorts, or full transaction behaviour; very model-centric | Not selected |

## Recommendation

Use Berka as the primary source and publish the **analysis code, data model, tests, and source instructions**, not the raw data. This yields the strongest evidence for the target roles. Keep UCI Bank Marketing as a documented fallback rather than mixing unrelated datasets into one story.

## Why not Olist

Olist is useful for marketplace operations, but it would repeat the familiar e-commerce orders/customers/payments portfolio pattern. Berka adds domain-specific banking questions, a many-to-many account/client relationship, longitudinal balances and transactions, product holdings, and credit outcomes. That makes it a better complement to an AI-product project and a stronger match for banking analytics and BI interviews.

## Primary references

- PKDD'99 original/archived description: <https://sorry.vse.cz/~berka/challenge/pkdd1999/berka.htm>
- PKDD'99 source archive: <https://sorry.vse.cz/~berka/challenge/pkdd1999/data_berka.zip>
- Current CTU Relational entry: <https://relational.fel.cvut.cz/dataset/Financial>
- Pinned acquisition mirror: <https://github.com/jlacko/berka-dataset>
- UCI Bank Marketing: <https://archive.ics.uci.edu/dataset/222/bank+marketing>
- UCI Default of Credit Card Clients: <https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients>
