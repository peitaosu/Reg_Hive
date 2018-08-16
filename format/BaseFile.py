from struct import unpack, pack

class BaseFile(object):

    def __init__(self, obj, off=0):
        self.obj = obj
        self.off = off
    
    def get_file_size(self):
        self.obj.seek(0, 2)
        return self.obj.tell()

    def read_bin(self, pos, len):
        self.obj.seek(self.off + pos)
        return self.obj.read(len)
    
    def write_bin(self, pos, data):
        self.obj.seek(self.off + pos)
        self.obj.write(data)
    
    def read_uint8(self, pos):
		b = self.read_bin(pos, 1)
		return unpack('<B', b)[0]

    def write_uint8(self, pos, i):
		b = pack('<B', i)
		self.write_bin(pos, b)

    def read_int8(self, pos):
		b = self.read_bin(pos, 1)
		return unpack('<b', b)[0]

    def write_int8(self, pos, i):
		b = pack('<b', i)
		self.write_bin(pos, b)

    def read_uint16(self, pos):
		b = self.read_bin(pos, 2)
		return unpack('<H', b)[0]

    def write_uint16(self, pos, i):
		b = pack('<H', i)
		self.write_bin(pos, b)

    def read_int16(self, pos):
		b = self.read_bin(pos, 2)
		return unpack('<h', b)[0]

    def write_int16(self, pos, i):
		b = pack('<h', i)
		self.write_bin(pos, b)

    def read_uint32(self, pos):
        b = self.read_bin(pos, 4)
        return unpack('<L', b)[0]

    def write_uint32(self, pos, i):
        b = pack('<L', i)
        self.write_bin(pos, b)

    def read_int32(self, pos):
        b = self.read_bin(pos, 4)
        return unpack('<l', b)[0]

    def write_int32(self, pos, i):
        b = pack('<l', i)
        self.write_bin(pos, b)

    def read_uint64(self, pos):
        b = self.read_bin(pos, 8)
        return unpack('<Q', b)[0]

    def write_uint64(self, pos, i):
        b = pack('<Q', i)
        self.write_bin(pos, b)
    
    def read_int64(self, pos):
        b = self.read_bin(pos, 8)
        return unpack('<q', b)[0]

    def write_int64(self, pos, i):
        b = pack('<q', i)
        self.write_bin(pos, b)
    
