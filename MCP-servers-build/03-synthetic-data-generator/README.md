# 03 - Synthetic Data Generator MCP

A FastMCP server that turns the [SDV (Synthetic Data Vault)](https://sdv.dev)
library into three LLM-callable tools: **generate**, **evaluate**, and
**visualize** synthetic tabular data for multi-table relational
datasets. Point any MCP host (Cursor, Claude Desktop, etc.) at it and
ask, in natural language, for a fake-but-realistic copy of your data.

## Project purpose

Make synthetic data generation a first-class capability that an LLM
agent can drive end-to-end: train a synthesizer on real CSVs, sample
new rows that preserve the joint distributions and table
relationships, score the result, and produce a column-level
sanity-check plot — all without the user touching the SDV API.

## Why synthetic data matters for AI development

- **Privacy & compliance.** You can share, demo, or open-source a
  dataset shaped exactly like the production one without leaking PII
  or violating GDPR/HIPAA.
- **Bigger training sets.** When real labeled data is scarce or
  expensive, sampling extra rows from a fitted synthesizer is a cheap
  way to augment a training set.
- **Safe testing environments.** CI pipelines, staging databases, and
  load tests need realistic-looking data; static fixtures get stale
  and rarely capture real correlations.
- **Reproducible experiments.** A synthesizer + a seed is a compact,
  versionable substitute for a multi-gigabyte dump.
- **Edge-case generation.** Once you have a model of the data, you can
  oversample rare conditions to stress-test downstream ML models.

SDV's `HMASynthesizer` handles the multi-table case: it learns the
distribution *and* the parent/child relationships described in
`metadata.json`, so foreign keys in the synthetic `orders.csv` still
point to valid synthetic `customers.csv` rows.

## The three tools

### 1. `sdv_generate(data_folder, num_rows_scale=1.0)`
Reads every `*.csv` in `data_folder`, loads `metadata.json`, fits an
`HMASynthesizer`, samples `scale * original_size` rows per table, and
writes the result to `data_folder/synthetic_data/`. Returns a summary
with the output folder and per-table row counts.

### 2. `sdv_evaluate(data_folder)`
Loads the real CSVs from `data_folder` and the synthetic CSVs from
`data_folder/synthetic_data/`, then runs SDV's
`evaluate_quality(...)`. Returns:
```json
{
  "overall_score": 0.87,
  "properties": [
    {"property": "Column Shapes",      "score": 0.91},
    {"property": "Column Pair Trends", "score": 0.83}
  ]
}
```

### 3. `sdv_visualize(data_folder, table_name, column_name)`
Calls SDV's `get_column_plot(...)` to overlay the real and synthetic
distributions for a single column, saves the figure to
`data_folder/plots/<table>_<column>.png`, and returns the path. If
`kaleido` isn't installed, it falls back to an interactive HTML file.

## File structure

```
03-synthetic-data-generator/
├── server.py            # Thin FastMCP wrappers, one tool per function
├── tools.py             # Real SDV logic — importable & testable on its own
├── sample_data/
│   ├── customers.csv    # 10 rows
│   ├── orders.csv       # 15 rows, FK → customers.customer_id
│   └── metadata.json    # Multi-table schema with the relationship
├── requirements.txt
├── cursor_config.json
└── README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```
SDV pulls in `copulas`, `rdt`, and friends, so the first install is
chunky. `kaleido` is optional but lets `sdv_visualize` produce PNGs;
without it the tool saves an HTML plot instead.

## How to run

```bash
python server.py
```
Listens on `http://127.0.0.1:8090/sse`.

## How to invoke each tool

Once the server is running you can drive it from any MCP host. Below
are example payloads — the host LLM will fill them in from natural
language like "generate twice as much synthetic data from the sample
folder".

**Generate**
```json
{
  "tool": "sdv_generate",
  "arguments": {
    "data_folder": "sample_data",
    "num_rows_scale": 2.0
  }
}
```
Result:
```json
{
  "output_folder": ".../sample_data/synthetic_data",
  "rows_per_table": {"customers": 20, "orders": 30},
  "tables": ["customers", "orders"]
}
```

**Evaluate**
```json
{
  "tool": "sdv_evaluate",
  "arguments": {"data_folder": "sample_data"}
}
```

**Visualize**
```json
{
  "tool": "sdv_visualize",
  "arguments": {
    "data_folder": "sample_data",
    "table_name": "customers",
    "column_name": "age"
  }
}
```
Returns `{"plot_path": ".../sample_data/plots/customers_age.png", "format": "png"}`.

## Connect to Cursor

Paste `cursor_config.json` into your Cursor `mcp.json`:
```json
{
  "mcpServers": {
    "synthetic-data-generator": {
      "url": "http://127.0.0.1:8090/sse",
      "transport": "sse"
    }
  }
}
```
Make sure `python server.py` is running first, then reload Cursor's
MCP panel.

## What does the quality score mean?

`evaluate_quality` returns a single number between **0.0 and 1.0**.
It's the average of two sub-scores:

- **Column Shapes** — for each column, how closely does the
  synthetic marginal distribution match the real one? (KS statistic
  for numerical columns, TV distance for categorical.)
- **Column Pair Trends** — for each pair of columns, how well are
  the real correlations / contingencies preserved in the synthetic
  data?

Rules of thumb:

| Score          | Interpretation                                          |
|----------------|---------------------------------------------------------|
| 0.90 - 1.00    | Excellent — synthetic data is nearly indistinguishable. |
| 0.80 - 0.90    | Good — fine for most testing / augmentation use cases.  |
| 0.70 - 0.80    | Fair — usable, but inspect the per-property breakdown.  |
| < 0.70         | Poor — likely needs more real data or model tuning.     |

The tiny 10/15-row sample dataset will not score 0.95 — it exists to
prove the pipeline runs end-to-end, not to show off SDV.

## What I learned

- **Separate MCP plumbing from business logic.** Putting the SDV code
  in `tools.py` and importing it from `server.py` means the same
  functions can be unit-tested with `pytest`, called from a notebook,
  or wrapped behind a totally different transport (CLI, REST, gRPC)
  without rewriting them. The MCP server becomes a thin adapter, not
  a god module.
- **Each `@mcp.tool` should be a one-liner.** When the body of a tool
  is just `return tools.generate(...)`, every change to the data
  pipeline lives in exactly one place, and the docstring stays the
  single source of truth for the LLM-facing contract.
- **Docstrings are still doing the routing.** Even with three tools
  from the same domain, "use this **after** sdv_generate" in
  `sdv_evaluate`'s docstring is what teaches the LLM the correct
  call order. Be explicit about preconditions in the description.
- **Side effects need a return value the LLM can reason about.** Each
  tool writes files to disk *and* returns a structured dict (output
  folder, scores, plot path). The dict is what flows back to the LLM
  so it can chain the next call ("now visualize the `age` column from
  the folder you just wrote to").
- **Multi-table SDV is mostly about `metadata.json`.** Almost all of
  the modeling power lives in the schema description — column
  sdtypes, primary keys, and relationships. Get the metadata right
  and `HMASynthesizer.fit` + `.sample` is two lines.
