from BaseBlock import BaseBlock

class KeyValue(BaseBlock):

	def __init__(self, buf):
		super(KeyValue, self).__init__(buf)
		signature = self.get_signature()

	def get_signature(self):
		return self.read_bin(0, 2)

	def get_value_name_length(self):
		return self.read_uint16(2)

	def get_data_size(self):
		return self.read_uint32(4)

	def get_data_size_real(self):
		size = self.get_data_size()
		if size >= 0x80000000:
			size -= 0x80000000

		return size

	def is_data_inline(self):
		return self.get_data_size() >= 0x80000000

	def get_inline_data(self):
		return self.read_bin(8, 4)

	def get_data_offset(self):
		return self.read_uint32(8)

	def get_data_type(self):
		return self.read_uint32(12)

	def get_flags(self):
		return self.read_uint16(16)

	def get_spare(self):
		return self.read_uint16(18)

	def get_title_index(self):
		return self.read_uint32(16)

	def get_value_name(self):
		return self.read_bin(20, self.get_value_name_length())

	def get_slack(self):
		return self.read_bin(20 + self.get_value_name_length())

class KeyValues(BaseBlock):

	def __init__(self, buf, elements_count):
		super(KeyValues, self).__init__(buf)
		self.elements_count = elements_count

	def elements(self):
		i = 0
		while i < self.elements_count:
			yield self.read_uint32(i * 4)
			i += 1

	def remnant_elements(self):
		i = self.elements_count
		while i < self.get_size() // 4:
			yield self.read_uint32(i * 4)
			i += 1

	def get_slack(self):
		return self.read_bin(self.elements_count * 4)
