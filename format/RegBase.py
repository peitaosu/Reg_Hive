from RegFile import RegFile

FILE_TYPE_PRIMARY = 0
MINOR_VERSION_NUMBERS_FOR_OLD_CELL_FORMAT = set([1])

class RegBase(RegFile):

    def __init__(self, obj):
        super(RegBase, self).__init__(obj)
        self.signature = self.get_signature()
        self.effective_root_cell_offset = self.get_root_cell_offset()
        self.effective_version = self.get_minor_version()
        self.effective_last_reorganized_timestamp = self.get_last_reorganized_timestamp()
        self.effective_flags = self.get_flags()
        self.use_old_cell_format = self.effective_version in MINOR_VERSION_NUMBERS_FOR_OLD_CELL_FORMAT
        self.is_primary_file = self.get_file_type() == FILE_TYPE_PRIMARY
        self.file_size = self.get_file_size()
        self.is_baseblock_valid = self.validate_checksum()
        self.is_file_dirty = self.get_primary_sequence_number() != self.get_secondary_sequence_number()
        self.effective_last_written_timestamp = self.get_last_written_timestamp()
        self.effective_hbins_data_size = self.get_hbins_data_size()


    def get_signature(self):
        return self.read_bin(0, 4)

    def get_primary_sequence_number(self):
        return self.read_uint32(4)

    def get_secondary_sequence_number(self):
        return self.read_uint32(8)

    def write_synchronized_sequence_numbers(self, sequence_number):
        self.write_uint32(4, sequence_number)
        self.write_uint32(8, sequence_number)

    def get_last_written_timestamp(self):
        return self.read_uint64(12)

    def get_major_version(self):
        return self.read_uint32(20)

    def get_minor_version(self):
        return self.read_uint32(24)

    def get_file_type(self):
        return self.read_uint32(28)

    def write_file_type(self, file_type):
        self.write_uint32(28, file_type)

    def get_file_format(self):
        return self.read_uint32(32)

    def get_root_cell_offset(self):
        return self.read_uint32(36)

    def get_hbins_data_size(self):
        return self.read_uint32(40)

    def write_hbins_data_size(self, hbins_data_size):
        self.write_uint32(40, hbins_data_size)

    def get_clustering_factor(self):
        return self.read_uint32(44)

    def get_filename(self):
        return self.read_bin(48, 64)

    def get_checksum(self):
        return self.read_uint32(508)

    def write_checksum(self, checksum):
        self.write_uint32(508, checksum)

    def get_boot_type(self):
        if not self.is_primary_file:
            return

        return self.read_uint32(4088)

    def get_boot_recover(self):
        if not self.is_primary_file:
            return

        return self.read_uint32(4092)

    def get_rmid(self):
        return self.read_bin(112, 16)

    def get_logid(self):
        return self.read_bin(128, 16)

    def get_flags(self):
        return self.read_uint32(144)

    def write_flags(self, flags):
        self.write_uint32(144, flags)

    def get_tmid(self):
        return self.read_bin(148, 16)

    def get_guid_signature(self):
        return self.read_bin(164, 4)

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

    def get_thawrmid(self):
        if not self.is_primary_file:
            return

        return self.read_bin(4056, 16)

    def get_thawlogid(self):
        if not self.is_primary_file:
            return

        return self.read_bin(4072, 16)

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
