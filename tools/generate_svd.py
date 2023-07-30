import argparse
import sys
import os
import git
import subprocess


def main():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--git-url",
        "-g",
        required=True,
        type=str,
        help="The git url of opentitan project.",
    )
    args_parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        required=True,
        type=str,
        help="The output file path. Default:./<top_level_name>.svd",
    )

    args = args_parser.parse_args()
    opentitan_dir = "/tmp/opentitan"
    print(f"cloning {args.git_url} to {opentitan_dir}")
    repo = git.Repo.clone_from(args.git_url, opentitan_dir, branch="master")

    print(f"generating svd")
    subprocess.run(
        [
            "python3",
            f"{os.path.dirname(__file__)}/hjson2svd.py",
            "-i",
            f"{opentitan_dir}/hw/top_earlgrey/data/top_earlgrey.hjson",
            "-o",
            args.output,
        ]
    )
    print("finished")


if __name__ == "__main__":
    sys.exit(main())
