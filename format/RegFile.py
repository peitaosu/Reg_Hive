from struct import unpack, pack

class RegFile():

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
    
