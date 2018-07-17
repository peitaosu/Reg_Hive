import os, sys, json

class Registry():

    def __init__(self):
        self.reg = {}
    
    def read_from_reg(self, reg_file_path):
        # suppose the input file using utf-16 because it's default encoding of regedit exported file
        try:
            with open(reg_file_path) as reg_file:    
                reg_str_list = reg_file.read().decode('utf-16').replace('\\\r\n  ', '').split('\r\n')
        except:
            with open(reg_file_path, encoding='utf-16') as reg_file:
                reg_str_list = reg_file.read().replace('\\\r\n  ', '').split('\r\n')
        reg_str_list = filter(None, reg_str_list)
        for reg_str in reg_str_list:
            if reg_str == 'Windows Registry Editor Version 5.00':
                continue
            if reg_str.startswith('['):
                reg_str = reg_str[1:-1]
                reg_root = reg_str.split('\\')[0]
                if reg_root not in self.reg:
                    self.reg[reg_root] = {
                        "Keys": {},
                        "Values": []
                        }
                cur_dict = self.reg[reg_root]
                for reg_key in reg_str.split('\\')[1:]:
                    if reg_key not in cur_dict['Keys'].keys():
                        cur_dict['Keys'][reg_key] = {
                            "Keys": {},
                            "Values": []
                        }
                        cur_dict = cur_dict['Keys'][reg_key]
                    else:
                        cur_dict = cur_dict['Keys'][reg_key]
                cur_key = cur_dict
            else:
                value_name = reg_str.split('=')[0].strip('"')
                if value_name == '@':
                    value_name = '(Default)'
                value_content = '='.join(reg_str.split('=')[1:])
                if value_content.startswith('"'):
                    value_type = "REG_SZ"
                    value_data = value_content.strip('"')
                elif value_content.startswith('dword'):
                    value_type = "REG_DWORD"
                    value_data = value_content.split(':')[1]
                elif value_content.startswith('qword'):
                    value_type = "REG_QWORD"
                    value_data = value_content.split(':')[1]
                elif value_content.startswith('hex'):
                    value_type = "REG_BINARY"
                    value_data = value_content.split(':')[1].replace(',', '')
                cur_key['Values'].append(
                    {
                        "Name": value_name,
                        "Type": value_type,
                        "Data": value_data
                    }
                )

    def dump_to_json(self, json_file_path):
        with open(json_file_path, 'w') as json_file:
            json.dump(self.reg, json_file, indent=4)

    def dump_to_reg(self, reg_file_path):
        reg_str_list = []
        reg_str_list.append('Windows Registry Editor Version 5.00')

        def parse_key(parent_key, parent_str):
            if len(parent_key['Values']) != 0:
                reg_str_list.append('\n[{}]'.format(parent_str))
            for value in parent_key['Values']:
                name = value['Name']
                if name is '(Default)':
                    name = '@'
                if value['Type'] is "REG_SZ":
                    reg_str_list.append('"{}"="{}"'.format(name, value['Data']))
                elif value['Type'] is "REG_DWORD":
                    reg_str_list.append('"{}"=dword:{}'.format(name, value['Data']))
                elif value['Type'] is "REG_QWORD":
                    reg_str_list.append('"{}"=qword:{}'.format(name, value['Data']))
                elif value['Type'] is "REG_BINARY":
                    reg_str_list.append('"{}"=hex:{}'.format(name, value['Data']))
            for key in parent_key['Keys']:
                parse_key(parent_key['Keys'][key], parent_str + '\\' + key)

        for root in self.reg:
            key_path = root
            cur_key = self.reg[root]
            parse_key(cur_key, key_path)
                    
        with open(reg_file_path, 'w') as reg_file:
            reg_file.write('\n'.join(reg_str_list))

if __name__=="__main__":
    reg = Registry()
    reg.read_from_reg(sys.argv[1])
    reg.dump_to_json(sys.argv[2])
    reg.dump_to_reg(sys.argv[3])