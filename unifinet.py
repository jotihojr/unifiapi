#!/usr/bin/env python3

from unifi import AuthNetRc, Arguments, UnifiApiClient


def parseCommandLine():
    import argparse
    import sys

    unifi = Arguments()
    sc = unifi.serverConnection()
    pp = unifi.setPoePortProfilePower()
    dp = unifi.cyclePoePortDevicePower()

    # bring all the argument groups together
    parsers = argparse.ArgumentParser(parents=[sc, pp, dp])
    args = parsers.parse_args()

    if unifi.missingAllOptionals(args):
        parsers.print_help(sys.stderr)
        sys.exit(1)
    return args


if __name__ == "__main__":
    argv = parseCommandLine()

    unifi = UnifiApiClient(argv.server, verify=argv.verify)
    unifi.login(AuthNetRc(argv.server))

    if argv.profile:
        unifi.setPoeModeByPortProfileName(name=argv.profile, poeMode=argv.mode)
    if argv.device:
        unifi.cyclePoePortPower(mac=argv.device, port=argv.port)

    unifi.logout()
