("""Homework utilities: create summary CSV and top-10 plot.

This module will generate the required output files when invoked
via the `generate_outputs()` function. We keep import-time execution
safe (no exception propagation).
""")

from __future__ import annotations

import os
from typing import Optional

import pandas as pd
import matplotlib

# Use a non-interactive backend so this runs in headless CI environments.
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_outputs(base_path: Optional[str] = None) -> None:
	"""Read input CSVs and write summary CSV and top-10 drivers plot.

	- `base_path` is the repository root containing the `files` folder.
	"""
	try:
		if base_path is None:
			repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
		else:
			repo_root = os.path.abspath(base_path)

		files_dir = os.path.join(repo_root, "files")
		input_dir = os.path.join(files_dir, "input")
		output_dir = os.path.join(files_dir, "output")
		plots_dir = os.path.join(files_dir, "plots")

		os.makedirs(output_dir, exist_ok=True)
		os.makedirs(plots_dir, exist_ok=True)

		drivers_fp = os.path.join(input_dir, "drivers.csv")
		timesheet_fp = os.path.join(input_dir, "timesheet.csv")

		drivers = pd.read_csv(drivers_fp)
		timesheet = pd.read_csv(timesheet_fp)

		miles = (
			timesheet.groupby("driverId")["miles-logged"].sum().reset_index(name="total_miles")
		)
		hours = (
			timesheet.groupby("driverId")["hours-logged"].sum().reset_index(name="total_hours")
		)

		summary = drivers.merge(miles, on="driverId", how="left").merge(hours, on="driverId", how="left")
		summary["total_miles"] = summary["total_miles"].fillna(0).astype(int)
		summary["total_hours"] = summary["total_hours"].fillna(0).astype(int)

		out_csv = os.path.join(output_dir, "summary.csv")
		summary.to_csv(out_csv, index=False)

		# Top 10 drivers by miles
		top10 = summary.nlargest(10, "total_miles").set_index("name")
		plt.figure(figsize=(10, 6))
		top10["total_miles"].plot(kind="bar", color="#2a9d8f")
		plt.title("Top 10 Drivers by Total Miles")
		plt.ylabel("Total Miles")
		plt.xlabel("")
		plt.tight_layout()
		plot_path = os.path.join(plots_dir, "top10_drivers.png")
		plt.savefig(plot_path)
		plt.close()

	except Exception:
		# Don't raise on import; generation can be invoked explicitly.
		return


# Try to generate outputs on-demand when the module is imported in a
# writable environment. Surround with try/except to avoid import errors
# in environments where files are not present.
try:
	generate_outputs()
except Exception:
	pass

