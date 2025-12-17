import sys

from descriptions.help_description import HELP_DESCRIPTION

def parse_flags():
    flags = {}

    if "--help" in sys.argv:
        print(HELP_DESCRIPTION)
        sys.exit(0)

    flags["verbose"] = "--verbose" in sys.argv
    flags["prompt"] = "--prompt" in sys.argv
    flags["no_tuning"] = "--no-tuning" in sys.argv
    flags["from_file"] = "--from-file" in sys.argv

    if flags["prompt"] and from_file:
        print("Can't use --from-file and --prompt flag together. Choose one.")
        sys.exit(1)

    args = {}
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if prompt:
        if len(args[0].strip()) < 1:
            print("Prompt too short. Exiting.")
            sys.exit(1)
        
        if verbose:
            print("User used flag --prompt. Skipping loading transcription from file")

    return flags, args