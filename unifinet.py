#!/usr/bin/env python3

from unifi import UnifiRestApi, PoeMode, MacAddr


def parseArgs():
    import argparse
    import sys

    pp = argparse.ArgumentParser(add_help=False, argument_default=None)
    pg = pp.add_argument_group(
        "Set POE Port Power",
        "Manipulate poe_mode of all ports associated to a specific port profile.",
    )
    pg.add_argument(
        "--profile", type=str, required=False, help="port profile name; (str)"
    )

    pga, _ = pp.parse_known_args()
    pg.add_argument(
        "--mode", type=PoeMode, required=pga.profile, help="poe mode; (off|auto)"
    )

    dp = argparse.ArgumentParser(add_help=False, argument_default=None)
    dg = dp.add_argument_group(
        "Cycle POE Port Power",
        "Cycle a single port poe_mode of the device specified with a MAC address.",
    )
    dg.add_argument(
        "--device",
        type=MacAddr,
        required=False,
        help="device MAC address; (xx:xx:xx:xx:xx:xx)",
    )
    dpa, _ = dp.parse_known_args()

    dg.add_argument(
        "--port", type=int, required=dpa.device, help="port number of device; (int)"
    )

    combined = argparse.ArgumentParser(parents=[pp, dp])
    args = combined.parse_args()
    if args.profile is None and args.device is None:
        combined.print_help(sys.stderr)
        sys.exit(1)
    return args


if __name__ == "__main__":
    argv = parseArgs()

    unifi = UnifiRestApi("unifi.holland.int", verify=False)
    unifi.login(netrcFile="~/.config/netrc")

    if argv.profile:
        unifi.setPoeModeByPortProfileName(name=argv.profile, poeMode=argv.mode)
    if argv.device:
        unifi.cyclePoePortPower(mac=argv.device, port=argv.port)

    unifi.logout()
