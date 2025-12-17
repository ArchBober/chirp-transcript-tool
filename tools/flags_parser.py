# * Handles --help, --verbose, --prompt, --no-tuning and --from-file.
# * Enforces that --prompt and --from-file cannot be used together.
# * Validates that a non-empty prompt is supplied when --prompt is used.
# * Returns a clear mapping of flags → arguments for downstream code.


import argparse
import sys

from typing import Tuple, Dict, List

from descriptions.help_description import HELP_DESCRIPTION


def _build_parser() -> argparse.ArgumentParser:
    """Create the ArgumentParser with all supported options."""
    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION,
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output."
    )
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Read the prompt from the command line (first positional arg)."
    )
    parser.add_argument(
        "--no-tuning",
        action="store_true",
        help="Skip any model-tuning steps."
    )
    parser.add_argument(
        "--from-file",
        metavar="PATH",
        type=str,
        help="Load the prompt from a file instead of the command line."
    )
    parser.add_argument(
        "--from-dir",
        metavar="PATH",
        type=str,
        help="Load the prompt from a file instead of the command line."
    )
    parser.add_argument(
        "--help",
        action="store_true",
        help="Show this help message and exit."
    )
    parser.add_argument(
        "positional",
        nargs="*",
        help="Additional arguments (e.g. the prompt text when --prompt is used)."
    )

    return parser


def parse_flags() -> Tuple[Dict[str, object], List[str]]:
    """
    Parse command-line arguments and return a tuple:

    * ``flags`` - a dict mapping flag names to their resolved values.
    * ``args``  - a list of leftover positional arguments.
    """
    parser = _build_parser()
    ns = parser.parse_args()

    if ns.help:
        print(HELP_DESCRIPTION)
        sys.exit(0)

    flags = {
        "verbose": ns.verbose,
        "prompt": ns.prompt,
        "no_tuning": ns.no_tuning,
        "from_file": ns.from_file,
        "from_dir": ns.from_dir,
    }

    if flags["prompt"] and (flags["from_file"] or flags["from_dir"]):
        print("Can't use --prompt with --from-file or --from-dir flag together. Choose one.")
        sys.exit(1)

    if flags["from_file"] and flags["from_dir"]:
        print("Can't use --from-file with --from-dir flag together. Choose one.")
        sys.exit(1)

    args = ns.positional

    if flags["prompt"]:
        if not args:
            print("Prompt missing. Exiting.")
            sys.exit(1)

        if len(args[0].strip()) < 1:
            print("Prompt too short. Exiting.")
            sys.exit(1)

        if flags["verbose"]:
            print("User used flag --prompt. Skipping loading transcription from file")

    return flags, args
    