#!/usr/bin/env python3

import argparse
from .easybake import SiteBuilder, serve, clean

parser = argparse.ArgumentParser(
    prog="easybake", description="Generate a static website"
)
parser.add_argument(
    "command", type=str, help="The action to take (e.g. build, serve)",
)
parser.add_argument("--site", type=str, help="The definition of the site to build")
parser.add_argument(
    "--templates", type=str, default="templates", help="the template directory"
)
parser.add_argument(
    "--content", type=str, default="content", help="the content directory"
)

args = parser.parse_args()

if args.command.lower() == "build":
    sb = SiteBuilder(args.site, template_dir=args.templates, content_dir=args.content)
    sb.build()
elif args.command.lower() == "serve":
    serve()
elif args.command.lower() == "clean":
    clean()
else:
    print("Unknown command '{}'".format(args.command))
