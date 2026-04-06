"""FastMCP server exposing the SDV synthetic-data tools.

Server logic stays thin: every tool is a one-line wrapper around a
function in `tools.py`. This keeps the MCP surface decoupled from the
data-science code so the latter can be tested or scripted on its own.

Run with:
    python server.py
The server listens on http://127.0.0.1:8090/sse
"""

from fastmcp import FastMCP

import tools

mcp = FastMCP("synthetic-data-generator")


@mcp.tool()
def sdv_generate(data_folder: str, num_rows_scale: float = 1.0) -> dict:
    """Train an SDV HMASynthesizer on a folder of related CSVs and generate synthetic data.

    Use this tool when the user wants to create synthetic / fake / mock
    tabular data that mirrors the statistical structure of their real
    multi-table dataset (for testing, sharing, or model training without
    leaking PII).

    Args:
        data_folder: Path to a folder containing one CSV per table and a
            `metadata.json` describing the schema and table relationships.
        num_rows_scale: Multiplier for how many synthetic rows to generate
            relative to the real data (1.0 = same size, 2.0 = twice as
            large, 0.5 = half).

    Returns:
        A dict with the output folder, the list of tables that were
        generated, and the row count for each.
    """
    return tools.generate(data_folder=data_folder, num_rows_scale=num_rows_scale)


@mcp.tool()
def sdv_evaluate(data_folder: str) -> dict:
    """Evaluate the quality of previously generated synthetic data.

    Use this tool after `sdv_generate` to measure how faithfully the
    synthetic CSVs reproduce the statistical properties of the real
    CSVs in the same folder.

    Args:
        data_folder: The same folder you passed to `sdv_generate`. The
            tool reads the real CSVs from this folder and the synthetic
            CSVs from its `synthetic_data/` subfolder.

    Returns:
        A dict with `overall_score` (0.0-1.0, higher is better) and a
        `properties` list breaking the score down into Column Shapes
        and Column Pair Trends.
    """
    return tools.evaluate(data_folder=data_folder)


@mcp.tool()
def sdv_visualize(data_folder: str, table_name: str, column_name: str) -> dict:
    """Plot a single column's real-vs-synthetic distribution and save it to disk.

    Use this tool when the user wants a visual sanity check that one
    specific column in the synthetic data matches the real data.

    Args:
        data_folder: The folder containing the real CSVs and the
            `synthetic_data/` subfolder.
        table_name: Which table to inspect (e.g. "customers").
        column_name: Which column inside that table to plot.

    Returns:
        A dict with `plot_path` pointing at the saved image (PNG by
        default, HTML fallback if static export is unavailable).
    """
    return tools.visualize(
        data_folder=data_folder,
        table_name=table_name,
        column_name=column_name,
    )


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8090)
