"""Download Sanskrit datasets for Skhand."""

import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "sanskrit"

DATASETS = [
    {
        "name": "Charaka Samhita (gita/Datasets)",
        "repo": "https://github.com/gita/Datasets.git",
        "target": DATA_DIR / "charaka-samhita",
        "sparse_paths": ["Charaka Samhita"],
    },
    {
        "name": "Digital Corpus of Sanskrit",
        "repo": "https://github.com/OliverHellwig/sanskrit.git",
        "target": DATA_DIR / "dcs",
        "sparse_paths": ["dcs/data/conllu"],
    },
]


def download_dataset(dataset: dict):
    """Clone a dataset repository using sparse checkout."""
    name = dataset["name"]
    repo = dataset["repo"]
    target = dataset["target"]
    sparse_paths = dataset.get("sparse_paths")

    if target.exists() and any(target.iterdir()):
        print(f"  [skip] {name} already exists at {target}")
        return

    target.mkdir(parents=True, exist_ok=True)

    print(f"  Downloading {name}...")

    if sparse_paths:
        # Use sparse checkout to only get needed files
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none",
             "--sparse", repo, str(target)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(target), "sparse-checkout", "set"] + sparse_paths,
            check=True,
        )
    else:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo, str(target)],
            check=True,
        )

    print(f"  [done] {name}")


def main():
    """Download all datasets."""
    print("Downloading Sanskrit datasets for Skhand...\n")

    for dataset in DATASETS:
        try:
            download_dataset(dataset)
        except subprocess.CalledProcessError as e:
            print(f"  [error] Failed to download {dataset['name']}: {e}")
        except Exception as e:
            print(f"  [error] {dataset['name']}: {e}")

    print("\nDone! Run 'skhand ingest sanskrit' to process the data.")


if __name__ == "__main__":
    main()
