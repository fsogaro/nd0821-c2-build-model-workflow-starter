#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning,
 exporting the result to a new artifact
"""
import os
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    project_name = "nyc_airbnb"
    try:
        logging.info(f'{os.environ["WANDB_PROJECT"]}')
    except:
        logging.info("could not find env var project")

    with wandb.init(project=project_name, group="development",
                    job_type="basic_cleaning") as run:
        run.config.update(args)

        # Download input artifact. This will also log that this script is using this
        # particular version of the artifact
        # artifact_local_path = run.use_artifact(args.input_artifact).file()
        logging.info("Retrieving input artifact for project nyc_airbnb with "
                 f"name {args.input_artifact}")
        ## YOUR CODE HERE
        artifact = run.use_artifact(args.input_artifact)
        local_path = artifact.file()
        df = pd.read_csv(local_path)

        logging.info("preprocessing steps for data cleaning")
        idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(
            40.5, 41.2)
        df = df[idx].copy().reset_index(drop=True)
        df = df.drop_duplicates().reset_index(drop=True)
        df = df.dropna().reset_index(drop=True)
        idx = df['price'].between(args.min_price, args.max_price)
        df = df[idx].copy()
        # Convert last_review to datetime
        df['last_review'] = pd.to_datetime(df['last_review'])
        # %%

        logging.info(f"Saving processed data as type: {args.output_type} "
                     f"with name {args.output_artifact} ")
        filename = args.output_artifact
        df.to_csv(filename, index=False)

        artifact = wandb.Artifact(
            name=filename,
            type=args.output_type,
            description=args.output_description,
        )
        artifact.add_file(filename)
        run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="name of artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="name to give to processed data",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="type of output file",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="output file description",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="minimum valid price to be set (int)",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="maximimum valid price to be set (int)",
        # HERE,
        required=True
    )


    args = parser.parse_args()

    go(args)
