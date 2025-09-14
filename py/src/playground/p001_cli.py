import argparse
from pathlib import Path
from playground.p002_utils import vectors_dir, results_dir


def cmd_hello(_args: argparse.Namespace) -> int:
    print("Hello from playground!")
    return 0


def cmd_io(args: argparse.Namespace) -> int:
    vin = Path(args.input) if args.input else vectors_dir() / "example.txt"
    vout = Path(args.output) if args.output else results_dir() / "out.txt"
    vout.write_text(vin.read_text())
    print(f"copied: {vin} -> {vout}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="play-cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("hello")
    sp.set_defaults(func=cmd_hello)

    sp = sub.add_parser("io")
    sp.add_argument("--input", "-i")
    sp.add_argument("--output", "-o")
    sp.set_defaults(func=cmd_io)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
