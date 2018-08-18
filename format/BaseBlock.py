from struct import unpack, pack

class BaseBlock():

	def __init__(self, buf):
		self.buf = buf

	def read_bin(self, pos, len = None):
		if len is None:
			return self.buf[pos : ]
		return self.buf[pos : pos + len]

	def read_uint8(self, pos):
		b = self.read_bin(pos, 1)
		return unpack('<B', b)[0]

	def read_uint16(self, pos):
		b = self.read_bin(pos, 2)
		return unpack('<H', b)[0]

	def read_uint32(self, pos):
		b = self.read_bin(pos, 4)
		return unpack('<L', b)[0]

	def read_uint64(self, pos):
		b = self.read_bin(pos, 8)
		return unpack('<Q', b)[0]

	def get_size(self):
		return len(self.buf)