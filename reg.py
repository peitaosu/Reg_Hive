import os, sys, json, uuid, optparse, difflib, platform, subprocess

class Registry():

    def __init__(self):
        self.reg = {}
        self.reg_str = []
        # suppose the input file using utf-16 because it's default encoding of regedit exported file
        self.reg_file_encode = "utf-16"
        self.regedit_ver = "Windows Registry Editor Version 5.00"
        self.log = "reg.log"
        self.regdat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regdat.exe")
    
    def set_log(self, log_path):
        """set path to log file

        args:
            log_path (str)
        """
        self.log = log_path
    
    def _log(self, log_str, print_to_console=True):
        """write log string to log file

        args:
            log_str (str)
            print_to_console (bool)
        """
        if print_to_console:
            print(log_str)
        with open(self.log, "a") as in_file:
            in_file.write("{}\n".format(log_str))

    def set_reg_file_encode(self, reg_file_encode):
        """update self.reg_file_encode which will be used to read *.reg file

        args:
            reg_file_encode (str)
        """
        self.reg_file_encode = reg_file_encode
    
    def set_regedit_ver(self, regedit_ver):
        """update self.regedit_ver which will be used in reg string

        args:
            regedit_ver (str)
        """
        self.regedit_ver = regedit_ver
    
    def set_reg(self, reg):
        """update self.reg which is a dictionary

        args:
            reg (dict)
        """
        self.reg = reg

    def get_reg(self):
        """get self.reg which is a dictionary

        returns:
            self.reg (dict)
        """
        return self.reg
    
    def get_reg_str(self):
        """get reg string which can be saved to *.reg
        
        returns:
            reg_str (list)
        """
        self.dump_to_reg()
        return self.reg_str
    
    def read_from_reg(self, reg_file_path):
        """read reg string from *.reg file and convert to dict type object - self.reg

        args:
            reg_file_path (str)
        """
        try:
            with open(reg_file_path) as reg_file:    
                self.reg_str = reg_file.read().decode(self.reg_file_encode).replace("\\\r\n  ", "").split("\r\n")
        except:
            with open(reg_file_path, encoding=self.reg_file_encode) as reg_file:
                self.reg_str = reg_file.read().replace("\\\r\n  ", "").split("\r\n")
        self.reg_str = filter(None, self.reg_str)
        for reg_str in self.reg_str:
            try:
                if reg_str == self.regedit_ver:
                    continue
                if reg_str.startswith("["):
                    reg_str = reg_str[1:-1]
                    reg_root = reg_str.split("\\")[0]
                    if reg_root not in self.reg:
                        self.reg[reg_root] = {
                            "Keys": {},
                            "Values": []
                            }
                    cur_dict = self.reg[reg_root]
                    for reg_key in reg_str.split("\\")[1:]:
                        if reg_key not in cur_dict["Keys"].keys():
                            cur_dict["Keys"][reg_key] = {
                                "Keys": {},
                                "Values": []
                            }
                            cur_dict = cur_dict["Keys"][reg_key]
                        else:
                            cur_dict = cur_dict["Keys"][reg_key]
                    cur_key = cur_dict
                else:
                    value_name = reg_str.split("=")[0].strip('"')
                    if value_name == "":
                        value_name = "@"
                    value_content = "=".join(reg_str.split("=")[1:])
                    if value_content.startswith('"'):
                        value_type = "REG_SZ"
                        value_data = value_content.strip('"')
                    elif value_content.startswith("dword"):
                        value_type = "REG_DWORD"
                        value_data = value_content.split(":")[1]
                    elif value_content.startswith("qword"):
                        value_type = "REG_QWORD"
                        value_data = value_content.split(":")[1]
                    elif value_content.startswith("hex:"):
                        value_type = "REG_BINARY"
                        value_data = value_content.split(":")[1]
                    elif value_content.startswith("hex(2)"):
                        value_type = "REG_EXPAND_SZ"
                        value_data = value_content.split(":")[1]
                    elif value_content.startswith("hex(7)"):
                        value_type = "REG_MULTI_SZ"
                        value_data = value_content.split(":")[1]
                    cur_key["Values"].append(
                        {
                            "Name": value_name,
                            "Type": value_type,
                            "Data": value_data
                        }
                    )
            except Exception as e:
                print("[Error] EXCEPTION ON {}: {}".format(reg_str, str(e)))

    def read_from_json(self, json_file_path):
        """read reg dict object from *.json file and update self.reg

        args:
            json_file_path (str)
        """
        with open(json_file_path) as json_file:
            self.reg = json.load(json_file)

    def read_from_dat(self, dat_file_path, hive_replace_key=None, hive_load_path=None):
        """read reg items from *.dat file and convert to dict type object - self.reg

        args:
            dat_file_path (str)
        """
        uuid_str = str(uuid.uuid4())
        temp_reg_file = uuid_str + ".reg"
        command = "regdat --dat2reg --in_dat {} --out_reg {}".format(dat_file_path, temp_reg_file)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        self._log("[REG] Output:{}".format(output))
        self.read_from_reg(temp_reg_file)
        os.remove(temp_reg_file)

    def dump_to_json(self, json_file_path):
        """dump dict type object self.reg to *.json file

        args:
            json_file_path (str)
        """
        with open(json_file_path, "w") as json_file:
            json.dump(self.reg, json_file, indent=4)

    def dump_to_reg(self, reg_file_path=None, dump_path=None):
        """convert and dump dict type object self.reg to *.reg file

        args:
            reg_file_path (str)
            dump_path (reg path)
        
        returns:
            reg_str (list)
        """
        self.reg_str = []
        self.reg_str.append(self.regedit_ver)

        def _parse_key(parent_key, parent_str):
            if len(parent_key["Values"]) != 0:
                self.reg_str.append("\n[{}]".format(parent_str))
            for value in sorted(parent_key["Values"], key=lambda k: k["Name"]):
                try:
                    if value["Type"] == "REG_SZ":
                        if value["Name"] == "@":
                            self.reg_str.append('@="{}"'.format(value["Data"]))
                        else:
                            self.reg_str.append('"{}"="{}"'.format(value["Name"], value["Data"]))
                    elif value["Type"] == "REG_DWORD":
                        self.reg_str.append('"{}"=dword:{}'.format(value["Name"], value["Data"]))
                    elif value["Type"] == "REG_QWORD":
                        self.reg_str.append('"{}"=qword:{}'.format(value["Name"], value["Data"]))
                    elif value["Type"] == "REG_BINARY":
                        self.reg_str.append('"{}"=hex:{}'.format(value["Name"], value["Data"]))
                    elif value["Type"] == "REG_EXPAND_SZ":
                        self.reg_str.append('"{}"=hex(2):{}'.format(value["Name"], value["Data"]))
                    elif value["Type"] == "REG_MULTI_SZ":
                        self.reg_str.append('"{}"=hex(7):{}'.format(value["Name"], value["Data"]))
                    else:
                        self.reg_str.append('"{}"="{}"'.format(value["Name"], value["Data"]))
                except Exception as e:
                    print("[Error] EXCEPTION ON {}: {}".format(value, str(e)))
            for key in sorted(parent_key["Keys"]):
                _parse_key(parent_key["Keys"][key], parent_str + "\\" + key)

        for root in self.reg:
            key_path = root
            cur_key = self.reg[root]
            _parse_key(cur_key, key_path)

        if dump_path is not None:
            started = False
            ended = False
            for iter in range(len(self.reg_str[1:])):
                if self.reg_str[1:][iter].startswith("\n[" + dump_path) and started == False:
                    started = iter
                if self.reg_str[1:][iter].startswith("\n[") and not self.reg_str[1:][iter].startswith("\n[" + dump_path) and started != False:
                    ended = iter
                    break
            if ended == False:
                matched_reg_str = self.reg_str[1:][started:]
            else:
                matched_reg_str = self.reg_str[1:][started:ended]
            if started == False and started != 0:
                print("[Error] {} PATH NOT FOUND.".format(dump_path))
                return None
            matched_reg_str = [self.regedit_ver] + matched_reg_str
        
        if reg_file_path is not None:  
            with open(reg_file_path, "w") as reg_file:
                if dump_path is None:
                    reg_file.write("\n".join(self.reg_str))
                    return self.reg_str
                else:
                    reg_file.write("\n".join(matched_reg_str))
                    return matched_reg_str

    def dump_to_dat(self, dat_file_path, dump_path, redirect_path = None):
        """convert and dump dict type object self.reg to *.dat file

        args:
            dat_file_path (str)
            dump_path (reg path)
            redirect_path (reg_path)
        
        returns:
            reg_str (list)
        """
        if len(self.reg_str) == 0:
            self.dump_to_reg()
        if dump_path is None:
            print("[Error] {} CANNOT BE NONE.".format("dump_path"))
            return None
        reg_root = dump_path.split("\\")[0]
        uuid_str = str(uuid.uuid4())
        dat_key = reg_root + "\\SOFTWARE\\" + uuid_str
        if redirect_path == None:
            redirect_path = dat_key
        else:
            redirect_path = dat_key + "\\" + redirect_path
        redirected_reg_str = []
        redirected_reg_str.append(self.regedit_ver)
        started = False
        ended = False
        for iter in range(len(self.reg_str[1:])):
            if self.reg_str[1:][iter].startswith("[" + dump_path) and started == False:
                started = iter
            if self.reg_str[1:][iter].startswith("[") and not self.reg_str[1:][iter].startswith("[" + dump_path) and started != False:
                ended = iter
                break
        if ended == False:
            matched_reg_str = self.reg_str[1:][started:]
        else:
            matched_reg_str = self.reg_str[1:][started:ended]
        if started == False and started != 0:
            print("[Error] {} PATH NOT FOUND.".format(dump_path))
            return None
        matched_reg_str = [x.replace(dump_path, redirect_path) for x in matched_reg_str]
        redirected_reg_str.extend(matched_reg_str)
        temp_reg_file = uuid_str + ".reg"
        with open(temp_reg_file, "w") as reg_file:
            reg_file.write("\n".join(redirected_reg_str))
        if platform.system() == "Windows":
            command = "reg import {}".format(temp_reg_file)
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            self._log("[REG] Output:{}".format(output))
            command = "reg save {} {} /y".format(dat_key, dat_file_path)
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            self._log("[REG] Output:{}".format(output))
            command = "reg delete {} /f".format(dat_key)
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            self._log("[REG] Output:{}".format(output))
        else:
            print("Only Windows supports registry, your OS is {}".format(platform.system()))
        os.remove(temp_reg_file)
        return redirected_reg_str
    
    def write_to_registry(self):
        """write registry keys\values to actual system registry
        """
        if platform.system() != "Windows":
            print("Only Windows supports registry, your OS is {}".format(platform.system()))
            return
        uuid_str = str(uuid.uuid4())
        temp_reg_file = uuid_str + ".reg"
        with open(temp_reg_file, "w") as reg_file:
            reg_file.write("\n".join(self.reg_str))
        command = "reg import {}".format(temp_reg_file)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        self._log("[REG] Output:{}".format(output))
        os.remove(temp_reg_file)

    def update_value(self, reg_root, reg_key, reg_value, new_reg_data):
        """update date of registry value

        args:
            reg_root (str)
            reg_key (str)
            reg_value (str)
            new_reg_data (str)
        """
        _key = self.reg[reg_root]
        for key in reg_key.split("\\"):
            _key = _key["Keys"][key]
        for value in _key["Values"]:
            if value["Name"] == reg_value:
                value["Data"] = new_reg_data

    def update_key_name(self, reg_root, reg_key, new_key_name):
        """update name of registry key

        args:
            reg_root (str)
            reg_key (str)
            new_key_name (str)
        """
        _key = self.reg[reg_root]
        for key in reg_key.split("\\")[:-1]:
            _key = _key["Keys"][key]
        _key["Keys"][new_key_name] = _key["Keys"].pop(reg_key.split("\\")[-1])
        
    def replace_with(self, origin, new):
        """replace specific string in reg object

        args:
            origin (str)
            new (str)
        """
        self.reg = json.loads(json.dumps(self.reg).replace(origin, new))
    
    def is_same(self, another):
        """check if same with another Registry object

        args:
            another (Registry)
        """
        return self.get_reg().__cmp__(another.get_reg()) == 0
    
    def compare_to(self, another, diff_file=None):
        """compare to another Registry object and save as diff file

        args:
            another (Registry)
            diff_file (str)
        
        returns:
            diff_result (list)
        """
        if self.is_same(another):
            return None
        differ = difflib.Differ()
        diff = differ.compare(self.get_reg_str(), another.get_reg_str())
        result = list(diff)
        length = len(result)
        for i in range(length):
            if not result[i].endswith("\n"):
                result[i] += "\n"
        if diff_file is not None:
            with open(diff_file, "w") as out_file:
                out_file.writelines(result)
        return result

def get_options():
    parser = optparse.OptionParser()
    parser.add_option("--in_reg", dest="in_reg",
                      help="read from reg file")
    parser.add_option("--in_json", dest="in_json",
                      help="read from json file")
    parser.add_option("--in_dat", dest="in_dat",
                      help="read from dat file")
    parser.add_option("--out_reg", dest="out_reg",
                      help="dump to reg file")
    parser.add_option("--reg_key", dest="reg_key",
                      help="reg key save to reg")
    parser.add_option("--out_json", dest="out_json",
                      help="dump to json file")
    parser.add_option("--out_dat", dest="out_dat",
                      help="dump to dat file")
    parser.add_option("--hive_key", dest="hive_key",
                      help="hive key save to dat")
    parser.add_option("--redirect", dest="redirect",
                      help="redirect dat key")
    parser.add_option("--load", dest="load",
                      help="load specific dat key")
    parser.add_option("--replace", dest="replace",
                      help="replace specific dat key")
    parser.add_option("--log", dest="log",
                      help="path to log file")
    (options, args) = parser.parse_args()
    return options

if __name__=="__main__":
    opt = get_options()

    reg = Registry()
    if opt.log:
        reg.set_log(opt.log)
    if opt.in_reg:
        reg.read_from_reg(opt.in_reg)
    if opt.in_json:
        reg.read_from_json(opt.in_json)
    if opt.in_dat:
        if opt.replace:
            if opt.load:
                reg.read_from_dat(opt.in_dat, opt.replace, opt.load)
            else:
                reg.read_from_dat(opt.in_dat, opt.replace)
        else:
            reg.read_from_dat(opt.in_dat)

    if opt.out_reg:
        reg.dump_to_reg(opt.out_reg, opt.reg_key)
    if opt.out_json:
        reg.dump_to_json(opt.out_json)
    if opt.out_dat:
        if opt.hive_key:
            if opt.redirect:
                reg.dump_to_dat(opt.out_dat, opt.hive_key, opt.redirect)
            else:
                reg.dump_to_dat(opt.out_dat, opt.hive_key, None)
        else:
            print("Please specify --hive_key.")
