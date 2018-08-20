from BaseBlock import BaseBlock
from collections import namedtuple

LeafElement = namedtuple('LeafElement', [ 'relative_offset', 'name_hint', 'name_hash' ])

class IndexLeaf(BaseBlock):
	def __init__(self, buf):
		super(IndexLeaf, self).__init__(buf)
		signature = self.get_signature()
		elements_count = self.get_elements_count()

	def get_signature(self):
		return self.read_bin(0, 2)

	def get_elements_count(self):
		return self.read_uint16(2)

	def elements(self):
		i = 0
		while i < self.get_elements_count():
			leaf_element = LeafElement(relative_offset = self.read_uint32(4 + i * 4), name_hint = None, name_hash = None)
			yield leaf_element
			i += 1

	def get_slack(self):
		return self.read_bin(4 + self.get_elements_count() * 4)

class FastLeaf(BaseBlock):
	def __init__(self, buf):
		super(FastLeaf, self).__init__(buf)
		signature = self.get_signature()
		elements_count = self.get_elements_count()

	def get_signature(self):
		return self.read_bin(0, 2)

	def get_elements_count(self):
		return self.read_uint16(2)

	def elements(self):
		i = 0
		while i < self.get_elements_count():
			leaf_element = LeafElement(relative_offset = self.read_uint32(4 + i * 8), name_hint = self.read_bin(4 + i * 8 + 4, 4), name_hash = None)
			yield leaf_element
			i += 1

	def get_slack(self):
		return self.read_bin(4 + self.get_elements_count() * 8)

class HashLeaf(BaseBlock):
	def __init__(self, buf):
		super(HashLeaf, self).__init__(buf)
		signature = self.get_signature()
		elements_count = self.get_elements_count()

	def get_signature(self):
		return self.read_bin(0, 2)

	def get_elements_count(self):
		return self.read_uint16(2)

	def elements(self):
		i = 0
		while i < self.get_elements_count():
			leaf_element = LeafElement(relative_offset = self.read_uint32(4 + i * 8), name_hash = self.read_uint32(4 + i * 8 + 4), name_hint = None)
			yield leaf_element
			i += 1

	def get_slack(self):
		return self.read_bin(4 + self.get_elements_count() * 8)

class IndexRoot(BaseBlock):
	def __init__(self, buf):
		super(IndexRoot, self).__init__(buf)
		signature = self.get_signature()
		elements_count = self.get_elements_count()

	def get_signature(self):
		return self.read_bin(0, 2)

	def get_elements_count(self):
		return self.read_uint16(2)

	def elements(self):
		i = 0
		while i < self.get_elements_count():
			yield self.read_uint32(4 + i * 4)
			i += 1

	def get_slack(self):
		return self.read_bin(4 + self.get_elements_count() * 4)
