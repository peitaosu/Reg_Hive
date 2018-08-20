from RegBlock import RegBlock
from RegLeaf import *

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


