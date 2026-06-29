#!/usr/bin/env python3
"""CLI entrypoint for building World Cup 2022 network analysis outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

from wc2022_networks.config import INPUT_DEFAULT, OUTPUT_DEFAULT
from wc2022_networks.outputs import write_outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    args = parser.parse_args()
    write_outputs(args.input, args.output)


if __name__ == "__main__":
    main()
