import math
import re


class OtRegGenIpParser:
    param_list: list
    data: dict
    offset: int
    quiet: bool

    def __init__(self, data: dict, quiet: bool):
        self.data = data
        self.reg_width = int(data["regwidth"])
        self.name = data["name"]
        self.offset = 0x40
        self.quiet = quiet

    def log(self, message: str):
        if not self.quiet:
            print(message)

    def parse_registers(self, peripheral):
        peripheral.add_address_block(0x000, 0x1000)
        registers = self.__get_registers()

        for reg in registers:
            if "multireg" in reg:
                self.parse_multireg(reg["multireg"], peripheral)
            elif "name" in reg:
                svd_reg = peripheral.add_register(reg["name"])
                self.parse_reg_fields(reg, svd_reg)
            elif "skipto" in reg:
                self.offset = int(reg["skipto"], 16)
            else:
                self.log(
                    """{}: Don't know how to parse register "{}", skipping it.""".format(self.name, list(reg.keys())[0])
                )

    def __get_registers(self):
        registers = self.data["registers"]
        if type(registers) is not list:
            registers = list()
            for key in self.data["registers"].keys():
                for reg in self.data["registers"][key]:
                    registers.append(reg)
        return registers

    def parse_multireg(self, reg, svd_peripheral):
        num_regs = self.evaluate_expression(reg["count"])
        if self.is_compact(reg):
            reg_width = self.get_bit_count(reg)
            total_width = num_regs * reg_width
            fields_per_reg = min(self.reg_width // reg_width, total_width)
            regs_count = math.ceil(num_regs / fields_per_reg)
            # self.log("{}.{} ".format(self.data["name"], reg["name"]))
            # self.log(f"\tMultireg: num_regs: {num_regs}, reg_width:{reg_width}, field_per_reg: {fields_per_reg}, regs_count: {regs_count}")

            for field_id in range(0, num_regs):
                if field_id % fields_per_reg == 0:
                    reg_id = math.ceil(field_id / fields_per_reg)
                    name = reg["name"] + (f"_{reg_id}" if regs_count > 1 else "")
                    svd_reg = svd_peripheral.add_register(name)

                self.parse_reg_fields(
                    reg,
                    svd_reg,
                    name_postfix=f"_{field_id}",
                    bit_offset=(field_id * reg_width) % self.reg_width,
                )

        else:
            for reg_id in range(0, num_regs):
                svd_reg = svd_peripheral.add_register("{}_{}".format(reg["name"], reg_id))
                self.parse_reg_fields(reg, svd_reg)

    def parse_reg_fields(self, reg, svd_reg, name_postfix: str = "", bit_offset: int = 0):
        svd_reg.add_description(reg["desc"])
        svd_reg.add_offset_address(self.offset)
        self.offset += self.reg_width // 8
        for field in reg["fields"]:
            name = field.get("name", "Value")
            svd_field = svd_reg.add_field(name + name_postfix)
            desc = field.get("desc", "Value")
            svd_field.add_description(desc)
            # resval = 0
            # if "resval" in field and field["resval"].isnumeric():
            #     resval = int(field["resval"])
            # svd_field.add_reset_value(resval)

            range = self.get_bit_range(field)
            svd_field.add_bit_range(range[1] + bit_offset, range[0] + bit_offset)
            permissions = reg.get("swaccess", "rw")
            svd_field.add_access_permission("r" in permissions, "w" in permissions)

    def get_bit_range(self, field):
        range = field["bits"].split(":")
        hi = range[0]
        lo = range[1] if len(range) > 1 else hi
        return self.evaluate_expression(hi), self.evaluate_expression(lo)

    def is_compact(self, reg):
        default_value = True if len(reg["fields"]) == 1 and not reg.get("regwen_multi", False) else False
        value = reg.get("compact", default_value)
        return value == "True" or value == "1" or value == True

    def evaluate_expression(self, expr: str) -> int:
        import re

        if expr.isnumeric():
            return int(expr)
        if "-" in expr:
            operands = expr.split("-", 1)
            return self.evaluate_expression(operands[0]) - self.evaluate_expression(operands[1])
        if "+" in expr:
            operands = expr.split("+", 1)
            return self.evaluate_expression(operands[0]) + self.evaluate_expression(operands[1])
        if re.match("[\w_]", expr):
            return int(self.get_param_val(expr))
        self.log(f"Could not evaluate : {expr}")

    def get_bit_count(self, reg):
        bits_count = 0
        for field in reg["fields"]:
            hi, lo = self.get_bit_range(field)
            bits_count += hi - lo + 1

        return bits_count

    def get_param_val(self, name: str):
        for param in self.data["param_list"]:
            if name == param["name"]:
                return param["default"]

        self.log(f"Could not find: {name}")
        return None
