import argparse
import os
import sys

from .typing import PoeMode, MacAddr


class Arguments:
    def __init__(self):
        self.__oneOf = []

    def __registerParameter(self, argument: str):
        self.__oneOf.append(argument)

    def missingAllOptionals(self, namespace: argparse.Namespace) -> bool:
        oneof = [param for param in self.__oneOf if not getattr(namespace, param)]
        if len(oneof) == len(self.__oneOf):
            prog = os.path.split(sys.argv[0])[-1]
            print(f"{prog}: command line missing all optional parameter groups")
            return True
        return False

    def setPoePortProfilePower(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False, argument_default=None)
        group = parser.add_argument_group(
            "Set POE Port Power (optional)",
            "Manipulate poe_mode of all ports associated to a specific port profile.",
        )
        optional = group.add_argument(
            "--profile", type=str, required=False, help="port profile name; (str)"
        )
        arg, _ = parser.parse_known_args()

        group.add_argument(
            "--mode", type=PoeMode, required=arg.profile, help="poe mode; (off|auto)"
        )

        self.__registerParameter(optional.dest)
        return parser

    def cyclePoePortDevicePower(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False, argument_default=None)
        group = parser.add_argument_group(
            "Cycle POE Port Power (optional)",
            "Cycle a single port poe_mode of the device specified with a MAC address.",
        )

        optional = group.add_argument(
            "--device",
            type=MacAddr,
            required=False,
            help="device MAC address; (xx:xx:xx:xx:xx:xx)",
        )
        arg, _ = parser.parse_known_args()

        group.add_argument(
            "--port", type=int, required=arg.device, help="port number of device; (int)"
        )

        self.__registerParameter(optional.dest)
        return parser

    def serverConnection(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        group = parser.add_argument_group(
            "Unifi API Server", "Determines the remote API server"
        )
        group.add_argument(
            "--server", type=str, default=None, required=True, help="server name or IP"
        )
        group.add_argument(
            "--noverify",
            dest="verify",
            action="store_false",
            help="no server verification",
        )
        return parser
