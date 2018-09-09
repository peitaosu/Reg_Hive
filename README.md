Registry Tool
===========

[![GitHub license](https://img.shields.io/github/license/peitaosu/Reg_Hive.svg)](https://github.com/peitaosu/Reg_Hive/blob/master/LICENSE)

Registry tool which support registry format conversion.

To use dat format file it request administrator permission to execute reg command.

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
  --out_json=OUT_JSON  dump to json file
  --out_dat=OUT_DAT    dump to dat file
  --reg_key=REG_KEY    reg key save to reg
  --hive_key=HIVE_KEY  hive key save to dat

```
