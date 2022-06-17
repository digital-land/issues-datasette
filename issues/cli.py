import csv
import glob
import os
import tempfile

import click
import requests
from dotenv import load_dotenv

load_dotenv()


collection_sql = """
SELECT c.collection, d.dataset
FROM collection c, dataset d
WHERE c.collection = d.collection;
"""


@click.command()
def load_issues():
    datasette_url = os.getenv("DATASETTE_URL", "https://datasette.digital-land.info")
    s3_url = os.getenv(
        "S3_URL",
        "https://digital-land-production-collection-dataset.s3.eu-west-2.amazonaws.com",
    )
    data_dir = f"{os.getcwd()}/data"
    with tempfile.TemporaryDirectory() as tmpdir:

        print("using datasette url", datasette_url)
        print("using digital land s3 collection bucket", s3_url)

        query = f"{datasette_url}/digital-land.json?sql={collection_sql.strip()}&_shape=array"

        resp = requests.get(query)
        resp.raise_for_status()
        data = resp.json()
        for row in data:
            collection = row["collection"]
            collection_bucket = f"{s3_url}/{collection}-collection"
            dataset = row["dataset"]
            dataset_csv_url = f"{collection_bucket}/dataset/{dataset}-issue.csv"
            download_dataset_issue_csv(tmpdir, dataset, dataset_csv_url)

        merge_csvs(data_dir, tmpdir)


def download_dataset_issue_csv(tmpdir, dataset, url):
    print("down loading", url)
    resp = requests.get(url)
    if resp.status_code == 200:
        csv_file = f"{tmpdir}/{dataset}-issue.csv"
        with open(csv_file, "w") as f:
            f.write(resp.text)
    print(url, "downloaded")


def merge_csvs(data_dir, tmpdir):
    fieldnames = [
        "dataset",
        "resource",
        "line-number",
        "entry-number",
        "field",
        "issue-type",
        "value",
    ]
    merged_file = os.path.join(data_dir, "dataset-issue.csv")

    with open(merged_file, "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for csv_file in glob.glob(f"{tmpdir}/*.csv"):
            dataset = csv_file.split("/")[-1].split("-issue.csv")[0]
            print("merging", csv_file, "for dataset", dataset)
            with open(csv_file, "r") as infile:
                reader = csv.DictReader(infile, fieldnames=fieldnames)
                for row in reader:
                    row["dataset"] = dataset
                    writer.writerow(row)

    print("done")


if __name__ == "__main__":
    load_issues()
