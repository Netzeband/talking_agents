import argparse
import asyncio
import logging
from dotenv import load_dotenv
from pathlib import Path

from src.talking_agents.create import create
from src.talking_agents.settings import Settings


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(override=True)
    settings = Settings()
    parser = argparse.ArgumentParser(description="Talking Agents creates audio files from arxiv papers.")
    parser.add_argument(
        "--episode-config-path",
        type=str,
        help="Path of the episode config yaml file.",
        required=True,
    )
    parser.add_argument(
        "--output-path",
        type=str,
        help="The output-path for the results.",
        required=True,
    )
    parser.add_argument(
        "--step",
        type=str,
        required=False,
        help="Defines optionally up to which step the podcast should be crated. The following steps are available: "
             "prepare, interview, post-processing (post-processing is the default)",
        default="post_processing",
    )
    args = parser.parse_args()
    asyncio.run(create(
        Path(args.episode_config_path),
        Path(args.output_path),
        args.step,
        settings,
    ))


if __name__ == "__main__":
    main()
