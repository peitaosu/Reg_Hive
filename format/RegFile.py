from BaseFile import BaseFile

FILE_TYPE_PRIMARY = 0
MINOR_VERSION_NUMBERS_FOR_OLD_CELL_FORMAT = set([1])

class RegFile(BaseFile):

    def __init__(self, obj):
        super(RegFile, self).__init__(obj)
        self.signature = self.get_signature()
        self.primary_sequence_number = self.get_primary_sequence_number()
        self.secondary_sequence_number = self.get_secondary_sequence_number()
        self.major_version = self.get_major_version()
        self.minor_version = self.get_minor_version()
        self.file_type = self.get_file_type()
        self.file_format = self.get_file_format()
        self.root_cell_offset = self.get_root_cell_offset()
        self.hbins_data_size = self.get_hbins_data_size()
        self.clustering_factor = self.get_clustering_factor()
        self.filename = self.get_filename()
        self.checksum = self.get_checksum()
        self.boot_type = self.get_boot_type()
        self.boot_recover = self.get_boot_recover()
        self.rmid = self.get_rmid()
        self.logid = self.get_logid()
        self.flags = self.get_flags()
        self.tmid = self.get_tmid()
        self.guid_signature = self.get_guid_signature()
        self.last_reorganized_timestamp = self.get_last_reorganized_timestamp()
        self.last_reorganized_type = self.get_last_reorganize_type()
        self.last_written_timestamp = self.get_last_written_timestamp()
        self.thawtmid = self.get_thawtmid()
        self.thawrmid = self.get_thawrmid()
        self.thawlogid = self.get_thawlogid()
        self.file_size = self.get_file_size()

        self.is_old_cell_format = self.get_minor_version() in MINOR_VERSION_NUMBERS_FOR_OLD_CELL_FORMAT
        self.is_primary_file = self.get_file_type() == FILE_TYPE_PRIMARY
        self.is_baseblock_valid = self.validate_checksum()
        self.is_file_dirty = self.get_primary_sequence_number() != self.get_secondary_sequence_number()


    def get_signature(self):
        return self.read_bin(0, 4)

    def write_signature(self, signature):
        self.write_bin(0, signature)
    
    def get_primary_sequence_number(self):
        return self.read_uint32(4)

    def write_primary_sequence_number(self, primary_sequence_number):
        self.write_uint32(4, primary_sequence_number)

    def get_secondary_sequence_number(self):
        return self.read_uint32(8)

    def write_secondary_sequence_number(self, secondary_sequence_number):
        self.write_uint32(8, secondary_sequence_number)

    def write_synchronized_sequence_numbers(self, sequence_number):
        self.write_uint32(4, sequence_number)
        self.write_uint32(8, sequence_number)

    def get_last_written_timestamp(self):
        return self.read_uint64(12)

    def write_last_written_timestamp(self, last_written_timestamp):
        self.write_uint64(12, last_written_timestamp)

    def get_major_version(self):
        return self.read_uint32(20)

    def write_major_version(self, major_version):
        self.write_uint32(20, major_version)

    def get_minor_version(self):
        return self.read_uint32(24)

    def write_minor_version(self, minor_version):
        self.write_uint32(24, minor_version)

    def get_file_type(self):
        return self.read_uint32(28)

    def write_file_type(self, file_type):
        self.write_uint32(28, file_type)

    def get_file_format(self):
        return self.read_uint32(32)

    def write_file_format(self, file_format):
        self.write_uint32(32, file_format)

    def get_root_cell_offset(self):
        return self.read_uint32(36)

    def write_root_cell_offset(self, root_cell_offset):
        self.write_uint32(36, root_cell_offset)

    def get_hbins_data_size(self):
        return self.read_uint32(40)
        
    def write_hbins_data_size(self, hbins_data_size):
        self.write_uint32(40, hbins_data_size)

    def get_clustering_factor(self):
        return self.read_uint32(44)

    def write_clustering_factor(self, clustering_factor):
        self.write_uint32(44, clustering_factor)

    def get_filename(self):
        return self.read_bin(48, 64)

    def write_filename(self, filename):
        self.write_bin(44, filename)

    def get_checksum(self):
        return self.read_uint32(508)

    def write_checksum(self, checksum):
        self.write_uint32(508, checksum)

    def get_boot_type(self):
        if not self.is_primary_file:
            return

        return self.read_uint32(4088)

    def write_boot_type(self, boot_type):
        self.write_uint32(4088, boot_type)

    def get_boot_recover(self):
        if not self.is_primary_file:
            return

        return self.read_uint32(4092)

    def write_boot_recover(self, boot_recover):
        self.write_uint32(4092, boot_recover)

    def get_rmid(self):
        return self.read_bin(112, 16)

    def write_rmid(self, rmid):
        self.write_bin(112, rmid)

    def get_logid(self):
        return self.read_bin(128, 16)

    def write_logid(self, logid):
        self.write_bin(128, logid)

    def get_flags(self):
        return self.read_uint32(144)

    def write_flags(self, flags):
        self.write_uint32(144, flags)

    def get_tmid(self):
        return self.read_bin(148, 16)

    def write_tmid(self, tmid):
        self.write_bin(148, tmid)

    def get_guid_signature(self):
        return self.read_bin(164, 4)

    def write_guid_signature(self, guid_signature):
        self.write_bin(164, guid_signature)

    def is_hive_rmtm(self):
        return self.get_guid_signature() == b'rmtm'

    def get_last_reorganized_timestamp(self):
        timestamp = self.read_uint64(168)
        if timestamp & 3 == 0 or timestamp & 3 == 3:
            return

        return timestamp

    def get_last_reorganize_type(self):
        timestamp = self.get_last_reorganized_timestamp()
        if timestamp is not None:
            return timestamp & 3

    def get_thawtmid(self):
        if not self.is_primary_file:
            return

        return self.read_bin(4040, 16)

    def write_thawtmid(self, thawtmid):
        self.write_bin(4040, thawtmid)

    def get_thawrmid(self):
        if not self.is_primary_file:
            return

        return self.read_bin(4056, 16)

    def write_thawrmid(self, thawrmid):
        self.write_bin(4056, thawrmid)

    def get_thawlogid(self):
        if not self.is_primary_file:
            return

        return self.read_bin(4072, 16)

    def write_thawlogid(self, thawlogid):
        self.write_bin(4072, thawlogid)

    def calculate_checksum(self):
        csum = 0

        i = 0
        while i < 508:
            cval = self.read_uint32(i)
            csum ^= cval
            i += 4

        if csum == 0:
            csum = 1
        elif csum == 0xFFFFFFFF:
            csum = 0xFFFFFFFE

        return csum

    def validate_checksum(self):
        return self.calculate_checksum() == self.get_checksum()

    def update_checksum(self):
        self.write_checksum(self.calculate_checksum())
