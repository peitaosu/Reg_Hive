Registry Tool
===========

[![GitHub license](https://img.shields.io/github/license/peitaosu/Reg_Hive.svg)](https://github.com/peitaosu/Reg_Hive/blob/master/LICENSE)

Registry tool which support registry format conversion.

Following operations request administrator permission to execute `reg` command:
* write registry to actual system

## Supported Formats:
* reg
* dat
* json

## Usage
```
> python reg.py -h

Usage: reg.py [options]

Options:
  -h, --help           show this help message and exit
  --in_reg=IN_REG      read from reg file
  --in_json=IN_JSON    read from json file
  --in_dat=IN_DAT      read from dat file
  --out_reg=OUT_REG    dump to reg file
  --reg_key=REG_KEY    reg key save to reg
  --out_json=OUT_JSON  dump to json file
  --out_dat=OUT_DAT    dump to dat file
  --hive_key=HIVE_KEY  hive key save to dat
  --redirect=REDIRECT  redirect dat key
  --load=LOAD          load specific dat key
  --replace=REPLACE    replace specific dat key
```

## Usage (module)
```
from reg import Registry

reg = Registry()
reg.set_reg_file_encode("utf-16")
reg.read_from_reg("example.reg")
reg.update_key_name("HKEY_LOCAL_MACHINE", "SOFTWARE\\Example", "SOFTWARE\\New_Key")
reg.update_value("HKEY_LOCAL_MACHINE", "SOFTWARE\\Example", "Example_Value", "New_Data")
reg.replace_with("ORIGINAL", "NEW")
reg.dump_to_json("out.json")
reg.dump_to_dat("out.dat")
```
