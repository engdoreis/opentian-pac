import os


class OtDirScheme:
    def __init__(self, top_level_file: str):
        base_dir = os.path.dirname(top_level_file)
        top_level_name = os.path.basename(top_level_file).split(".")[0]
        self.ip_path_tamplate = base_dir + "/../../ip/{ip}/data/{ip}.hjson"
        self.ip_autogen_path_tamplate = base_dir + "/../ip_autogen/{ip}/data/{ip}.hjson"
        self.ip_autogen2_path_tamplate = base_dir + "/../ip/{ip}/data/{ip}.hjson"
        self.top_gen_path = base_dir + "/autogen/" + top_level_name + ".gen.hjson"

    def get_ip_path(self, name: str) -> str:
        path = self.ip_path_tamplate.format(ip=name)
        if not os.path.exists(path):
            path = self.ip_autogen_path_tamplate.format(ip=name)
        if not os.path.exists(path):
            path = self.ip_autogen2_path_tamplate.format(ip=name)
        return path

    def get_top_gen_path(self):
        return self.top_gen_path
