#!/usr/bin/env python3

from unifi import UnifiRestApi, PoeMode, MacAddr


def parseCommandLine():
    import argparse
    import sys

    # port profile poe poer power
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

    # cycle power of a single poe port
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

    # server connection details
    sp = argparse.ArgumentParser(add_help=False)
    sg = sp.add_argument_group("Unifi API Server", "Determines the remote API server")
    sg.add_argument(
        "--server", type=str, default=None, required=True, help="server name or IP"
    )
    sg.add_argument(
        "--noverify", dest="verify", action="store_false", help="no server verification"
    )

    # bring all the argument groups together
    combined = argparse.ArgumentParser(parents=[sp, pp, dp])
    args = combined.parse_args()
    if args.profile is None and args.device is None:
        combined.print_help(sys.stderr)
        sys.exit(1)
    return args


if __name__ == "__main__":
    argv = parseCommandLine()

    unifi = UnifiRestApi(argv.server, verify=argv.verify)
    unifi.login(netrcFile="~/.config/netrc")

    if argv.profile:
        unifi.setPoeModeByPortProfileName(name=argv.profile, poeMode=argv.mode)
    if argv.device:
        unifi.cyclePoePortPower(mac=argv.device, port=argv.port)

    unifi.logout()
