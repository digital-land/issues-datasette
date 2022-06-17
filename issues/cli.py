import os
import subprocess
import tempfile
from pathlib import Path

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
    current_path = Path(os.path.realpath(__file__))
    data_dir = f"{current_path.parent.parent}/data"
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

        make_datasette_db(data_dir, tmpdir)


def download_dataset_issue_csv(tmpdir, dataset, url):
    print("downloading", url)
    resp = requests.get(url)
    if resp.status_code == 200:
        csv_file = f"{tmpdir}/{dataset}-issue.csv"
        with open(csv_file, "w") as f:
            f.write(resp.text)
        message = f"{url} downloaded"
    else:
        message = f"{url} not downloaded"
    return message


def make_datasette_db(data_dir, tmpdir):
    print("making issue datasette database")
    subprocess.run(
        [
            f"csvs-to-sqlite -i dataset,resource  {tmpdir}/*.csv {data_dir}/dataset-issue.sqlite3"
        ],
        shell=True,
        check=True,
    )
    subprocess.run(
        [
            f"datasette inspect {data_dir}/dataset-issue.sqlite3 --inspect-file {data_dir}/dataset-issue.json"
        ],
        shell=True,
        check=True,
    )
    print("done")


if __name__ == "__main__":
    load_issues()
