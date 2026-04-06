"""Business logic for the synthetic data MCP server.

Kept deliberately separate from `server.py` so the same functions can
be unit-tested, scripted, or reused without depending on FastMCP.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.io as pio
from sdv.evaluation.multi_table import evaluate_quality, get_column_plot
from sdv.metadata import Metadata
from sdv.multi_table import HMASynthesizer


def _load_tables(folder: Path) -> dict[str, pd.DataFrame]:
    """Load every CSV in `folder` into a dict keyed by file stem."""
    tables: dict[str, pd.DataFrame] = {}
    for csv_path in sorted(folder.glob("*.csv")):
        tables[csv_path.stem] = pd.read_csv(csv_path)
    if not tables:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    return tables


def _load_metadata(folder: Path) -> Metadata:
    metadata_path = folder / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"metadata.json not found in {folder}")
    return Metadata.load_from_json(str(metadata_path))


def generate(data_folder: str, num_rows_scale: float = 1.0) -> dict:
    """Train an HMASynthesizer on the CSVs in `data_folder` and write synthetic copies.

    The synthetic CSVs are written to `<data_folder>/synthetic_data/`.
    Returns a summary dict with the output folder and per-table row counts.
    """
    folder = Path(data_folder).resolve()
    real_tables = _load_tables(folder)
    metadata = _load_metadata(folder)

    synthesizer = HMASynthesizer(metadata)
    synthesizer.fit(real_tables)
    synthetic_tables = synthesizer.sample(scale=num_rows_scale)

    out_dir = folder / "synthetic_data"
    out_dir.mkdir(exist_ok=True)

    written: dict[str, int] = {}
    for name, df in synthetic_tables.items():
        out_path = out_dir / f"{name}.csv"
        df.to_csv(out_path, index=False)
        written[name] = len(df)

    return {
        "output_folder": str(out_dir),
        "rows_per_table": written,
        "tables": list(written.keys()),
    }


def evaluate(data_folder: str) -> dict:
    """Compare real CSVs in `data_folder` with synthetic CSVs in `synthetic_data/`.

    Returns the overall SDV quality score plus the per-property breakdown
    (Column Shapes and Column Pair Trends).
    """
    folder = Path(data_folder).resolve()
    synthetic_folder = folder / "synthetic_data"
    if not synthetic_folder.exists():
        raise FileNotFoundError(
            f"{synthetic_folder} does not exist - run sdv_generate first"
        )

    real_tables = _load_tables(folder)
    synthetic_tables = _load_tables(synthetic_folder)
    metadata = _load_metadata(folder)

    quality_report = evaluate_quality(
        real_data=real_tables,
        synthetic_data=synthetic_tables,
        metadata=metadata,
    )

    properties_df = quality_report.get_properties()
    properties = [
        {"property": row["Property"], "score": float(row["Score"])}
        for _, row in properties_df.iterrows()
    ]

    return {
        "overall_score": float(quality_report.get_score()),
        "properties": properties,
    }


def visualize(data_folder: str, table_name: str, column_name: str) -> dict:
    """Build a real-vs-synthetic column comparison plot and save it as PNG."""
    folder = Path(data_folder).resolve()
    synthetic_folder = folder / "synthetic_data"

    real_tables = _load_tables(folder)
    synthetic_tables = _load_tables(synthetic_folder)
    metadata = _load_metadata(folder)

    if table_name not in real_tables:
        raise KeyError(f"Table '{table_name}' not found in {folder}")
    if column_name not in real_tables[table_name].columns:
        raise KeyError(
            f"Column '{column_name}' not in table '{table_name}'"
        )

    fig = get_column_plot(
        real_data=real_tables,
        synthetic_data=synthetic_tables,
        metadata=metadata,
        table_name=table_name,
        column_name=column_name,
    )

    plots_dir = folder / "plots"
    plots_dir.mkdir(exist_ok=True)
    out_path = plots_dir / f"{table_name}_{column_name}.png"

    try:
        pio.write_image(fig, str(out_path), format="png")
    except Exception as exc:  # pragma: no cover - kaleido optional
        # Fall back to HTML so the user still gets something usable.
        out_path = out_path.with_suffix(".html")
        fig.write_html(str(out_path))
        return {
            "plot_path": str(out_path),
            "format": "html",
            "note": (
                "PNG export failed (install `kaleido` for static images). "
                f"Saved interactive HTML instead. Underlying error: {exc}"
            ),
        }

    return {"plot_path": str(out_path), "format": "png"}
