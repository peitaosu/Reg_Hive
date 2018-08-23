from KeyValue import *
from Utils import *
from struct import unpack, pack

REG_NONE                       = 0x00000000
REG_SZ                         = 0x00000001
REG_EXPAND_SZ                  = 0x00000002
REG_BINARY                     = 0x00000003
REG_DWORD                      = 0x00000004
REG_DWORD_LITTLE_ENDIAN        = REG_DWORD
REG_DWORD_BIG_ENDIAN           = 0x00000005
REG_LINK                       = 0x00000006
REG_MULTI_SZ                   = 0x00000007
REG_RESOURCE_LIST              = 0x00000008
REG_FULL_RESOURCE_DESCRIPTOR   = 0x00000009
REG_RESOURCE_REQUIREMENTS_LIST = 0x0000000a
REG_QWORD                      = 0x0000000b
REG_QWORD_LITTLE_ENDIAN        = REG_QWORD

VALUE_COMP_NAME = 0x0001
VALUE_TOMBSTONE = 0x0002

ValueTypes = {
    REG_NONE: 'REG_NONE',
    REG_SZ: 'REG_SZ',
    REG_EXPAND_SZ: 'REG_EXPAND_SZ',
    REG_BINARY: 'REG_BINARY',
    REG_DWORD: 'REG_DWORD',
    REG_DWORD_BIG_ENDIAN: 'REG_DWORD_BIG_ENDIAN',
    REG_LINK: 'REG_LINK',
    REG_MULTI_SZ: 'REG_MULTI_SZ',
    REG_RESOURCE_LIST: 'REG_RESOURCE_LIST',
    REG_FULL_RESOURCE_DESCRIPTOR: 'REG_FULL_RESOURCE_DESCRIPTOR',
    REG_RESOURCE_REQUIREMENTS_LIST: 'REG_RESOURCE_REQUIREMENTS_LIST',
    REG_QWORD: 'REG_QWORD'
}

class RegValue(object):
	registry_file = None
	key_value = None

	def __init__(self, primary_file, buf, naive = False):
		self.registry_file = primary_file
		if not naive:
			self.get_cell = self.registry_file.get_cell
		else:
			self.get_cell = self.registry_file.get_cell_naive

		self.key_value = KeyValue(buf)
		self.cell_relative_offset = None

	def name(self):
		name_buf = self.key_value.get_value_name()
		is_ascii = self.registry_file.baseblock.effective_version > 1 and self.key_value.get_flags() & VALUE_COMP_NAME > 0
		if is_ascii:
			return DecodeASCII(name_buf)

		return DecodeUnicode(name_buf)

	def type_raw(self):
		return self.key_value.get_data_type()

	def type_str(self):
		value_type = self.key_value.get_data_type()
		if value_type in ValueTypes.keys():
			return ValueTypes[value_type]
		else:
			return hex(value_type)

	def data_size(self):
		return self.key_value.get_data_size_real()

	def data_raw(self):
		if self.key_value.get_data_size_real() == 0:
			return b''

		if self.key_value.is_data_inline():
			return self.key_value.get_inline_data()[ : self.key_value.get_data_size_real()]

		is_big_data = self.registry_file.baseblock.effective_version > 3 and self.key_value.get_data_size_real() > 16344
		if not is_big_data:
			return self.get_cell(self.key_value.get_data_offset())[ : self.key_value.get_data_size_real()]

		big_data_buf = self.get_cell(self.key_value.get_data_offset())
		big_data = BigData(big_data_buf)

		segments_list_offset = big_data.get_segments_list_offset()
		segments_count = big_data.get_segments_count()

		segments_list = SegmentsList(self.get_cell(segments_list_offset), segments_count)

		data = b''
		data_length = self.key_value.get_data_size_real()
		for segment_offset in segments_list.elements():
			buf = self.get_cell(segment_offset)

			if data_length > 16344:
				data_part = buf[ : 16344]
				data += data_part
				data_length -= 16344
			else:
				data += buf[ : data_length]
				break

		return data

	def data_slack(self):
		if self.key_value.get_data_size_real() == 0 or self.key_value.is_data_inline():
			return []

		is_big_data = self.registry_file.baseblock.effective_version > 3 and self.key_value.get_data_size_real() > 16344
		if not is_big_data:
			slack = self.get_cell(self.key_value.get_data_offset())[self.key_value.get_data_size_real() : ]
			return [slack]

		slack_list = []

		big_data_buf = self.get_cell(self.key_value.get_data_offset())
		big_data = BigData(big_data_buf)

		slack_list.append(big_data.get_slack())

		segments_list_offset = big_data.get_segments_list_offset()
		segments_count = big_data.get_segments_count()

		segments_list = SegmentsList(self.get_cell(segments_list_offset), segments_count)

		slack_list.append(segments_list.get_slack())

		data_length = self.key_value.get_data_size_real()
		for segment_offset in segments_list.elements():
			buf = self.get_cell(segment_offset)

			if data_length > 16344:
				slack = buf[16344 : ]
				slack_list.append(slack)
				data_length -= 16344
			else:
				slack = buf[data_length : ]
				slack_list.append(slack)
				break

		return slack_list

	def data(self):
		data_raw = self.data_raw()
		data_length = len(data_raw)
		type_int = self.type_raw()

		if type_int == REG_DWORD and data_length == 4:
			return unpack('<L', data_raw)[0]

		if type_int == REG_DWORD_BIG_ENDIAN and data_length == 4:
			return unpack('>L', data_raw)[0]

		if type_int == REG_QWORD and data_length == 8:
			return unpack('<Q', data_raw)[0]

		if (type_int == REG_SZ or type_int == REG_EXPAND_SZ) and data_length % 2 == 0 and data_length > 1:
			return DecodeUnicode(data_raw, True)

		if type_int == REG_LINK and data_length % 2 == 0 and data_length > 1:
			return DecodeUnicode(data_raw, True)

		if type_int == REG_MULTI_SZ and data_length % 2 == 0 and data_length > 1:
			sz_list_data = DecodeUnicodeMulti(data_raw, True)
			if sz_list_data == '\x00':
				return []

			if len(sz_list_data) > 2 and sz_list_data[-1] == '\x00' and sz_list_data[-2] == '\x00':
				sz_list = sz_list_data[ : -1].split('\x00')

				i = 0
				while i < len(sz_list):
					sz_list[i] += '\x00'
					i += 1

				return sz_list

		return data_raw
