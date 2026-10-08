"""BitGov MAS-I1 reference validator CLI (proving harness only).

Usage:
    python reference_validator.py <projection.json>
    python reference_validator.py <projection.json> --attempted-use <use.json>

Prints the final-reliance result as JSON. Exit status 0 always (the verdict
is data, not a process failure); failures to read/parse inputs exit 2.
Non-normative reference implementation.
"""

from __future__ import annotations

import argparse
import json
import sys

from reference_proving_slice import (
    aegis_check,
    attempt_from_binding,
    final_reliance,
    gwo_bind,
    load_projection_file,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a BitGov MAS-I1 authorization projection.")
    parser.add_argument("projection", help="Path to projection JSON file.")
    parser.add_argument("--attempted-use", default=None,
                        help="Path to attempted-use JSON file "
                             "({principal, action, resource, context, scope}).")
    parser.add_argument("--bind", action="store_true",
                        help="Also run the reference GWO binder.")
    parser.add_argument("--aegis-capability", default=None,
                        help="Path to narrowed-capability JSON file for the "
                             "reference Aegis checker.")
    args = parser.parse_args(argv)

    try:
        projection = load_projection_file(args.projection)
    except (OSError, ValueError) as exc:
        print("input error: %s" % exc, file=sys.stderr)
        return 2

    attempted_use = None
    if args.attempted_use is not None:
        try:
            with open(args.attempted_use, "r", encoding="utf-8") as fh:
                attempted_use = json.load(fh)
        except (OSError, ValueError) as exc:
            print("input error: %s" % exc, file=sys.stderr)
            return 2

    output = {"final_reliance": final_reliance(projection, attempted_use)}
    if args.bind:
        output["gwo_bind"] = gwo_bind(
            projection,
            attempted_use if attempted_use is not None
            else attempt_from_binding(projection)
            if isinstance(projection, dict) else {})
    if args.aegis_capability is not None:
        try:
            with open(args.aegis_capability, "r", encoding="utf-8") as fh:
                capability = json.load(fh)
        except (OSError, ValueError) as exc:
            print("input error: %s" % exc, file=sys.stderr)
            return 2
        output["aegis_check"] = aegis_check(projection, capability)

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
