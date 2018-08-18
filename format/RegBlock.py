from BaseBlock import BaseBlock

class RegBlock(BaseBlock):


	def __init__(self, buf):
		super(RegBlock, self).__init__(buf)
		self.signature = self.get_signature()
		self.flags = self.get_flags()
		self.last_written_timestamp = self.get_last_written_timestamp()
		self.spare_1 = self.get_spare_1()
		self.title_index = self.get_title_index()
		self.access_bits = self.get_access_bits()
		self.layered_key_bit_fields = self.get_layered_key_bit_fields()
		self.spare_2 = self.get_spare_2()
		self.parent = self.get_parent()
		self.subkeys_count = self.get_subkeys_count()
		self.volatile_subkeys_count = self.get_volatile_subkeys_count()
		self.subkeys_list_offset = self.get_subkeys_list_offset()
		self.volatile_subkeys_list_offset = self.get_volatile_subkeys_list_offset()
		self.key_values_count = self.get_key_values_count()
		self.key_values_list_offset = self.get_key_values_list_offset()
		self.key_security_offset = self.get_key_security_offset()
		self.classname_offset = self.get_classname_offset()
		self.largest_subkey_name_length = self.get_largest_subkey_name_length()
		self.virtualization_control_and_user_flags = self.get_virtualization_control_and_user_flags()
		self.user_flags_old = self.get_user_flags_old()
		self.user_flags_new = self.get_user_flags_new()
		self.virtualization_control_flags = self.get_virtualization_control_flags()
		self.debug = self.get_debug()
		self.largest_subkey_classname_length = self.get_largest_subkey_classname_length()
		self.largest_value_name_length = self.get_largest_value_name_length()
		self.largest_value_data_size = self.get_largest_value_data_size()
		self.workvar = self.get_workvar()
		self.key_name_length = self.get_key_name_length()
		self.classname_length = self.get_classname_length()
		self.key_name = self.get_key_name()
		self.slack = self.get_slack()

	def get_signature(self):
		return self.read_bin(0, 2)

	def get_flags(self):
		return self.read_uint16(2)

	def get_last_written_timestamp(self):
		return self.read_uint64(4)

	def get_spare_1(self):
		return self.read_uint32(12)

	def get_title_index(self):
		return self.read_uint32(12)

	def get_access_bits(self):
		return self.read_uint8(12)

	def get_layered_key_bit_fields(self):
		return self.read_uint8(13)

	def get_spare_2(self):
		return self.read_uint16(14)

	def get_parent(self):
		return self.read_uint32(16)

	def get_subkeys_count(self):
		return self.read_uint32(20)

	def get_volatile_subkeys_count(self):
		return self.read_uint32(24)

	def get_subkeys_list_offset(self):
		return self.read_uint32(28)

	def get_volatile_subkeys_list_offset(self):
		return self.read_uint32(32)

	def get_key_values_count(self):
		return self.read_uint32(36)

	def get_key_values_list_offset(self):
		return self.read_uint32(40)

	def get_key_security_offset(self):
		return self.read_uint32(44)

	def get_classname_offset(self):
		return self.read_uint32(48)

	def get_largest_subkey_name_length(self):
		return self.read_uint16(52)

	def get_virtualization_control_and_user_flags(self):
		return self.read_uint8(54)

	def get_user_flags_old(self):
		return self.get_flags() >> 12

	def get_user_flags_new(self):
		return self.get_virtualization_control_and_user_flags() & 0xF

	def get_virtualization_control_flags(self):
		return self.get_virtualization_control_and_user_flags() >> 4

	def get_debug(self):
		return self.read_uint8(55)

	def get_largest_subkey_classname_length(self):
		return self.read_uint32(56)

	def get_largest_value_name_length(self):
		return self.read_uint32(60)

	def get_largest_value_data_size(self):
		return self.read_uint32(64)

	def get_workvar(self):
		return self.read_uint32(68)

	def get_key_name_length(self):
		return self.read_uint16(72)

	def get_classname_length(self):
		return self.read_uint16(74)

	def get_key_name(self):
		return self.read_bin(76, self.get_key_name_length())

	def get_slack(self):
		return self.read_bin(76 + self.get_key_name_length())
