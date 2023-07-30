import argparse
import sys

import hjson
from cmsis_svd_codec import SvdDevice
from Ot_hjson.OtRegGenIpParser import OtRegGenIpParser
from OtDirScheme import OtDirScheme


def main():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--input",
        "-i",
        metavar="FILE",
        required=True,
        type=str,
        help="The HJSON file that describes the top level.",
    )
    args_parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        required=False,
        type=str,
        help="The output file path. Default:./<top_level_name>.svd",
    )
    args_parser.add_argument(
        "--quiet",
        "-q",
        action=argparse.BooleanOptionalAction,
        help="Quiet mode, no debug messages",
    )

    args = args_parser.parse_args()
    with open(args.input) as p:
        top_level_data = hjson.load(p)

    device = SvdDevice("lowRISC", top_level_data["name"], "0.1")
    device.add_description("Single core 3-stage pipeline RISC-V processor ...")
    device.add_license(
        """Copyright lowRISC contributors.
                       Licensed under the Apache License, Version 2.0, see LICENSE for details.
                       SPDX-License-Identifier: Apache-2.0"""
    )

    device.add_cpu("ibex", "rev01", 2)
    device.add_address_config(width=top_level_data["datawidth"])

    path_scheme = OtDirScheme(args.input)

    with open(path_scheme.get_top_gen_path()) as p:
        top_gen_data = hjson.load(p)
    irq_list = top_gen_data["interrupt_module"]

    previous_type: str = None
    # white_list = ["uart", "i2c", "gpio", "pwm", "spi_host", "rv_timer", "alert_handler", "usb_dev"]
    # white_list = ["spi_device"]
    for ip in top_level_data["module"]:
        # if ip["type"] not in white_list:
        # continue
        ip_name = ip["name"]

        with open(path_scheme.get_ip_path(ip["type"])) as p:
            ip_data = hjson.load(p)

        derive_from = previous_type.upper() + "0" if previous_type == ip["type"] else None
        previous_type = ip["type"]

        version = ip_data["version"] if "version" in ip_data else ip_data["revisions"][-1]["version"]

        peripheral = device.add_peripheral(ip_name.upper(), version, derive_from)
        peripheral.add_description(ip_data.get("one_line_desc", ip_name))

        base_addr = ip.get("base_addr")
        if base_addr == None:
            possible_keys = ["core", "regs"]
            key = set(possible_keys) & set(ip["base_addrs"].keys())
            base_addr = ip["base_addrs"][key.pop()]

        peripheral.add_base_address(int(base_addr, 16))

        peripheral.add_size(int(ip_data["regwidth"]))

        irq_num = irq_list.index(ip["name"]) + 1 if ip["name"] in irq_list else 0
        peripheral.add_interrupt(irq_num)

        if derive_from == None:
            parser = OtRegGenIpParser(ip_data, args.quiet)
            parser.parse_registers(peripheral)

    output_file = f'./{top_level_data["name"]}.svd'
    if args.output:
        output_file = args.output
    device.dump(output_file)
    if not args.quiet:
        print(f"Generated {output_file}")


if __name__ == "__main__":
    sys.exit(main())
