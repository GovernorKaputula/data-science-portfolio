"""Run one study or reproduce the full portfolio: python run.py all."""
import argparse
import os
# Avoid oversubscribing small data workloads; set before importing numerical libraries.
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
from src.common import style, provenance
from src import demand, campaign, segments

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("study", choices=["all", "demand", "campaign", "segments"])
    args = parser.parse_args()
    style()
    for name, module in [("demand", demand), ("campaign", campaign), ("segments", segments)]:
        if args.study in [name, "all"]:
            print(f"Running {name}...", flush=True)
            result = module.run()
            print(f"Completed {name}: {result['rows']:,} rows", flush=True)
    if args.study == "all":
        provenance()

if __name__ == "__main__":
    main()
