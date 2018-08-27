from RegBlock import RegBlock
from RegFile import RegFile
from RegLeaf import *
from RegValue import *
from KeyValue import *
from Utils import *

class RegKey(object):

	def __init__(self, reg_file, buf, layer, cell_relative_offset, tolerate_minor_errors = False, naive = False):

		self.registry_file = reg_file
		self.naive = naive
		if not self.naive:
			self.get_cell = self.registry_file.get_cell
		else:
			self.get_cell = self.registry_file.get_cell_naive

		self.key_node = RegBlock(buf)
		self.cell_relative_offset = cell_relative_offset
		self.layer = layer
		self.tolerate_minor_errors = tolerate_minor_errors
		self.effective_slack = set()

	def last_written_timestamp(self):
		return self.key_node.get_last_written_timestamp()

	def access_bits(self):
		return self.key_node.get_access_bits()

	def name(self):
		return self.key_node.get_key_name()

	def classname(self):
		classname_length = self.key_node.get_classname_length()
		if classname_length > 0:
			classname_buf = self.get_cell(self.key_node.get_classname_offset())
			return classname_buf[ : classname_length]

	def parent(self):
		if self.layer == 0:
			return

		parent_offset = self.key_node.get_parent()
		parent_buf = self.get_cell(parent_offset)

		layer_up = None
		if self.layer is not None:
			layer_up = self.layer - 1

		parent_key_node = RegKey(self.registry_file, parent_buf, layer_up, parent_offset, self.tolerate_minor_errors, self.naive)

		return parent_key_node

	def path(self, show_root = False):
		path_components = [ self.name() ]

		if self.naive:
			track = set()
			track.add(self.key_node.get_parent())

		p = self.parent()
		while p is not None:
			if self.naive:
				p_parent = p.key_node.get_parent()
				track.add(p_parent)
			path_components.append(p.name())
			p = p.parent()

		path_components.reverse()
		if not show_root:
			path_components = path_components[ 1 : ]

		return '\\'.join(path_components)

	def subkeys(self):

		subkeys_names = set()

		def process_leaf(leaf_buf):
			leaf_signature = leaf_buf[ : 2]

			if leaf_signature == b'li':
				leaf = IndexLeaf(leaf_buf)
			elif leaf_signature == b'lf':
				leaf = FastLeaf(leaf_buf)
			else:
				leaf = HashLeaf(leaf_buf)

			slack = leaf.get_slack()
			self.effective_slack.add(slack)

			layer_down = None
			if self.layer is not None:
				layer_down = self.layer + 1

			if type(leaf) is IndexLeaf:
				for leaf_element in leaf.elements():
					subkey_offset = leaf_element.relative_offset

					buf = self.get_cell(subkey_offset)
					subkey = RegKey(self.registry_file, buf, layer_down, subkey_offset, self.tolerate_minor_errors, self.naive)
					yield subkey

			if type(leaf) is FastLeaf:
				for leaf_element in leaf.elements():
					subkey_offset = leaf_element.relative_offset

					buf = self.get_cell(subkey_offset)
					subkey = RegKey(self.registry_file, buf, layer_down, subkey_offset, self.tolerate_minor_errors, self.naive)
					yield subkey

			if type(leaf) is HashLeaf:
				for leaf_element in leaf.elements():
					subkey_offset = leaf_element.relative_offset

					buf = self.get_cell(subkey_offset)
					subkey = RegKey(self.registry_file, buf, layer_down, subkey_offset, self.tolerate_minor_errors, self.naive)
					yield subkey

		if self.key_node.get_subkeys_count() > 0:
			list_offset = self.key_node.get_subkeys_list_offset()
			list_buf = self.get_cell(list_offset)
			list_signature = list_buf[ : 2]
			prev_name = None

			if list_signature == b'ri':
				index_root = IndexRoot(list_buf)
				slack = index_root.get_slack()
				self.effective_slack.add(slack)

				for leaf_offset in index_root.elements():
					list_buf = self.get_cell(leaf_offset)
					for subkey in process_leaf(list_buf):
						curr_name = subkey.name().upper()
						if curr_name not in subkeys_names:
							subkeys_names.add(curr_name)
						prev_name = curr_name
						yield subkey
			else:
				for subkey in process_leaf(list_buf):
					curr_name = subkey.name().upper()
					if curr_name not in subkeys_names:
						subkeys_names.add(curr_name)
					prev_name = curr_name

					yield subkey
		
	def subkey(self, name):
		name = name.lower()
		for curr_subkey in self.subkeys():
			curr_name = curr_subkey.name().lower()
			if name == curr_name:
				return curr_subkey


	def values(self):
		values_names = set()
		values_count = self.values_count()
		if values_count > 0:
			list_offset = self.key_node.get_key_values_list_offset()
			list_buf = self.get_cell(list_offset)

			values_list = KeyValues(list_buf, values_count)

			slack = values_list.get_slack()
			self.effective_slack.add(slack)

			for value_offset in values_list.elements():
				buf = self.get_cell(value_offset)
				curr_value = RegValue(self.registry_file, buf, self.naive)
				curr_value.cell_relative_offset = value_offset

				slack_list = curr_value.data_slack()
				for curr_slack in slack_list:
					self.effective_slack.add(curr_slack)

				curr_name = curr_value.name().lower()
				if curr_name not in values_names:
					values_names.add(curr_name)

				yield curr_value

	def values_count(self):
		return self.key_node.get_key_values_count()
	
	def value(self, name = ''):
		name = name.lower()
		for curr_value in self.values():
			curr_name = curr_value.name().lower()
			if name == curr_name:
				return curr_value

class RegHive(object):
	registry_file = None
	log_entry_callback = None
	effective_slack = None

	def __init__(self, file_obj, tolerate_minor_errors = True):
		self.registry_file = RegFile(file_obj)
		self.tolerate_minor_errors = tolerate_minor_errors
		self.effective_slack = set()

	def root_key(self):
		return RegKey(self.registry_file, self.registry_file.get_root_cell_offset(), 0, self.registry_file.get_root_cell_offset(), self.tolerate_minor_errors)

	def last_written_timestamp(self):
		return DecodeFiletime(self.registry_file.get_last_written_timestamp())

	def last_reorganized_timestamp(self):
		timestamp = self.registry_file.get_last_reorganized_timestamp()
		if timestamp is not None:
			return DecodeFiletime(timestamp)

	def find_key(self, path):
		if path == '\\' or len(path) == 0:
			return self.root_key()
		if path[0] == '\\':
			path = path[1 : ]
		current_key = self.root_key()
		path_components = path.split('\\')
		i = 0
		while i < len(path_components) and current_key is not None:
			current_key = current_key.subkey(path_components[i])
			i += 1
		return current_key
