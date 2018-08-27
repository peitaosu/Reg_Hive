from datetime import *

def DecodeASCII(Buffer):
	return Buffer.decode('latin-1')

def DecodeUnicode(Buffer, RemoveGarbage = False, StrictDecode = False):
	if StrictDecode:
		err_resolution = 'strict'
	else:
		err_resolution = 'replace'

	if RemoveGarbage and len(Buffer) > 2:
		pos = 0
		while pos < len(Buffer):
			two_bytes = Buffer[pos : pos + 2]
			if two_bytes == b'\x00\x00':
				return Buffer[ : pos + 2].decode('utf-16le', errors = err_resolution)
			pos += 2

	return Buffer.decode('utf-16le', errors = err_resolution)

def DecodeUnicodeMulti(Buffer, RemoveGarbage = False):
	if RemoveGarbage and len(Buffer) > 4:
		pos = 0
		while pos < len(Buffer):
			four_bytes = Buffer[pos : pos + 4]
			if four_bytes == b'\x00\x00\x00\x00':
				return DecodeUnicode(Buffer[ : pos + 4])
			pos += 2

	return DecodeUnicode(Buffer)

def DecodeFiletime(Timestamp):
	return datetime(1601, 1, 1) + timedelta(microseconds = Timestamp / 10)
