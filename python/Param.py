"""
Copyright 2008, 2009 Free Software Foundation, Inc.
This file is part of GNU Radio

GNU Radio Companion is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

GNU Radio Companion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import expr_utils
from .. base.Param import Param as _Param
from .. gui.Param import Param as _GUIParam
from .. gui.Param import EntryParam
import Constants
import numpy
import os
import pygtk
pygtk.require('2.0')
import gtk
from gnuradio import eng_notation
import re
from gnuradio import gr

_check_id_matcher = re.compile('^[a-z|A-Z]\w*$')
_show_id_matcher = re.compile('^(variable\w*|parameter|options|notebook)$')

class FileParam(EntryParam):
	"""Provide an entry box for filename and a button to browse for a file."""

	def __init__(self, *args, **kwargs):
		EntryParam.__init__(self, *args, **kwargs)
		input = gtk.Button('...')
		input.connect('clicked', self._handle_clicked)
		self.pack_start(input, False)

	def _handle_clicked(self, widget=None):
		"""
		If the button was clicked, open a file dialog in open/save format.
		Replace the text in the entry with the new filename from the file dialog.
		"""
		#get the paths
		file_path = self.param.is_valid() and self.param.get_evaluated() or ''
		(dirname, basename) = os.path.isfile(file_path) and os.path.split(file_path) or (file_path, '')
		if not os.path.exists(dirname): dirname = os.getcwd() #fix bad paths
		#build the dialog
		if self.param.get_type() == 'file_open':
			file_dialog = gtk.FileChooserDialog('Open a Data File...', None,
				gtk.FILE_CHOOSER_ACTION_OPEN, ('gtk-cancel',gtk.RESPONSE_CANCEL,'gtk-open',gtk.RESPONSE_OK))
		elif self.param.get_type() == 'file_save':
			file_dialog = gtk.FileChooserDialog('Save a Data File...', None,
				gtk.FILE_CHOOSER_ACTION_SAVE, ('gtk-cancel',gtk.RESPONSE_CANCEL, 'gtk-save',gtk.RESPONSE_OK))
			file_dialog.set_do_overwrite_confirmation(True)
			file_dialog.set_current_name(basename) #show the current filename
		file_dialog.set_current_folder(dirname) #current directory
		file_dialog.set_select_multiple(False)
		file_dialog.set_local_only(True)
		if gtk.RESPONSE_OK == file_dialog.run(): #run the dialog
			file_path = file_dialog.get_filename() #get the file path
			self.entry.set_text(file_path)
			self._handle_changed()
		file_dialog.destroy() #destroy the dialog

#blacklist certain ids, its not complete, but should help
import __builtin__
ID_BLACKLIST = ['self', 'options', 'gr', 'blks2', 'wxgui', 'wx', 'math', 'forms', 'firdes'] + \
	filter(lambda x: not x.startswith('_'), dir(gr.top_block())) + dir(__builtin__)
#define types, native python + numpy
VECTOR_TYPES = (tuple, list, set, numpy.ndarray)
COMPLEX_TYPES = [complex, numpy.complex, numpy.complex64, numpy.complex128]
REAL_TYPES = [float, numpy.float, numpy.float32, numpy.float64]
INT_TYPES = [int, long, numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.uint64,
	numpy.uint, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]
#cast to tuple for isinstance, concat subtypes
COMPLEX_TYPES = tuple(COMPLEX_TYPES + REAL_TYPES + INT_TYPES)
REAL_TYPES = tuple(REAL_TYPES + INT_TYPES)
INT_TYPES = tuple(INT_TYPES)

class Param(_Param, _GUIParam):

	def __init__(self, **kwargs):
		_Param.__init__(self, **kwargs)
		_GUIParam.__init__(self)
		self._init = False
		self._hostage_cells = list()

	def get_types(self): return (
		'raw', 'enum',
		'complex', 'real', 'int',
		'complex_vector', 'real_vector', 'int_vector',
		'hex', 'string', 'bool',
		'file_open', 'file_save',
		'id', 'stream_id',
		'grid_pos', 'notebook',
		'import',
	)

	def __repr__(self):
		"""
		Get the repr (nice string format) for this param.
		@return the string representation
		"""
		if not self.is_valid(): return self.get_value()
		if self.get_value() in self.get_option_keys(): return self.get_option(self.get_value()).get_name()
		##################################################
		# display logic for numbers
		##################################################
		def num_to_str(num):
			if isinstance(num, COMPLEX_TYPES):
				num = complex(num) #cast to python complex
				if num == 0: return '0' #value is zero
				elif num.imag == 0: return '%s'%eng_notation.num_to_str(num.real) #value is real
				elif num.real == 0: return '%sj'%eng_notation.num_to_str(num.imag) #value is imaginary
				elif num.imag < 0: return '%s-%sj'%(eng_notation.num_to_str(num.real), eng_notation.num_to_str(abs(num.imag)))
				else: return '%s+%sj'%(eng_notation.num_to_str(num.real), eng_notation.num_to_str(num.imag))
			else: return str(num)
		##################################################
		# split up formatting by type
		##################################################
		truncate = 0 #default center truncate
		max_len = max(27 - len(self.get_name()), 3)
		e = self.get_evaluated()
		t = self.get_type()
		if isinstance(e, bool): return str(e)
		elif isinstance(e, COMPLEX_TYPES): dt_str = num_to_str(e)
		elif isinstance(e, VECTOR_TYPES): #vector types
			if len(e) > 8:
				dt_str = self.get_value() #large vectors use code
				truncate = 1
			else: dt_str = ', '.join(map(num_to_str, e)) #small vectors use eval
		elif t in ('file_open', 'file_save'):
			dt_str = self.get_value()
			truncate = -1
		else: dt_str = str(e) #other types
		##################################################
		# truncate
		##################################################
		if len(dt_str) > max_len:
			if truncate < 0: #front truncate
				dt_str = '...' + dt_str[3-max_len:]
			elif truncate == 0: #center truncate
				dt_str = dt_str[:max_len/2 -3] + '...' + dt_str[-max_len/2:]
			elif truncate > 0: #rear truncate
				dt_str = dt_str[:max_len-3] + '...'
		return dt_str

	def get_input(self, *args, **kwargs):
		if self.get_type() in ('file_open', 'file_save'): return FileParam(*args, **kwargs)
		return _GUIParam.get_input(self, *args, **kwargs)

	def get_color(self):
		"""
		Get the color that represents this param's type.
		@return a hex color code.
		"""
		try:
			return {
				#number types
				'complex': Constants.COMPLEX_COLOR_SPEC,
				'real': Constants.FLOAT_COLOR_SPEC,
				'int': Constants.INT_COLOR_SPEC,
				#vector types
				'complex_vector': Constants.COMPLEX_VECTOR_COLOR_SPEC,
				'real_vector': Constants.FLOAT_VECTOR_COLOR_SPEC,
				'int_vector': Constants.INT_VECTOR_COLOR_SPEC,
				#special
				'bool': Constants.INT_COLOR_SPEC,
				'hex': Constants.INT_COLOR_SPEC,
				'string': Constants.BYTE_VECTOR_COLOR_SPEC,
				'id': Constants.ID_COLOR_SPEC,
				'stream_id': Constants.ID_COLOR_SPEC,
				'grid_pos': Constants.INT_VECTOR_COLOR_SPEC,
				'notebook': Constants.INT_VECTOR_COLOR_SPEC,
				'raw': Constants.WILDCARD_COLOR_SPEC,
			}[self.get_type()]
		except: return _Param.get_color(self)

	def get_hide(self):
		"""
		Get the hide value from the base class.
		Hide the ID parameter for most blocks. Exceptions below.
		If the parameter controls a port type, vlen, or nports, return part.
		If the parameter is an empty grid position, return part.
		These parameters are redundant to display in the flow graph view.
		@return hide the hide property string
		"""
		hide = _Param.get_hide(self)
		if hide: return hide
		#hide ID in non variable blocks
		if self.get_key() == 'id' and not _show_id_matcher.match(self.get_parent().get_key()): return 'part'
		#hide port controllers for type and nports
		if self.get_key() in ' '.join(map(
			lambda p: ' '.join([p._type, p._nports]), self.get_parent().get_ports())
		): return 'part'
		#hide port controllers for vlen, when == 1
		if self.get_key() in ' '.join(map(
			lambda p: p._vlen, self.get_parent().get_ports())
		):
			try:
				assert int(self.get_evaluated()) == 1
				return 'part'
			except: pass
		#hide empty grid positions
		if self.get_key() in ('grid_pos', 'notebook') and not self.get_value(): return 'part'
		return hide

	def validate(self):
		"""
		Validate the param.
		A test evaluation is performed
		"""
		_Param.validate(self) #checks type
		self._evaluated = None
		try: self._evaluated = self.evaluate()
		except Exception, e: self.add_error_message(str(e))

	def get_evaluated(self): return self._evaluated

	def evaluate(self):
		"""
		Evaluate the value.
		@return evaluated type
		"""
		self._init = True
		self._lisitify_flag = False
		self._stringify_flag = False
		self._hostage_cells = list()
		def eval_string(v):
			try:
				e = self.get_parent().get_parent().evaluate(v)
				assert isinstance(e, str)
				return e
			except:
				self._stringify_flag = True
				return v
		t = self.get_type()
		v = self.get_value()
		#########################
		# Enum Type
		#########################
		if self.is_enum(): return v
		#########################
		# Numeric Types
		#########################
		elif t in ('raw', 'complex', 'real', 'int', 'complex_vector', 'real_vector', 'int_vector', 'hex', 'bool'):
			#raise exception if python cannot evaluate this value
			try: e = self.get_parent().get_parent().evaluate(v)
			except Exception, e: raise Exception, 'Value "%s" cannot be evaluated: %s'%(v, e)
			#raise an exception if the data is invalid
			if t == 'raw': return e
			elif t == 'complex':
				try: assert isinstance(e, COMPLEX_TYPES)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type complex.'%str(e)
				return e
			elif t == 'real':
				try: assert isinstance(e, REAL_TYPES)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type real.'%str(e)
				return e
			elif t == 'int':
				try: assert isinstance(e, INT_TYPES)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type integer.'%str(e)
				return e
			#########################
			# Numeric Vector Types
			#########################
			elif t == 'complex_vector':
				if not isinstance(e, VECTOR_TYPES):
					self._lisitify_flag = True
					e = [e]
				try:
					for ei in e: assert isinstance(ei, COMPLEX_TYPES)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type complex vector.'%str(e)
				return e
			elif t == 'real_vector':
				if not isinstance(e, VECTOR_TYPES):
					self._lisitify_flag = True
					e = [e]
				try:
					for ei in e: assert isinstance(ei, REAL_TYPES)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type real vector.'%str(e)
				return e
			elif t == 'int_vector':
				if not isinstance(e, VECTOR_TYPES):
					self._lisitify_flag = True
					e = [e]
				try:
					for ei in e: assert isinstance(ei, INT_TYPES)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type integer vector.'%str(e)
				return e
			elif t == 'hex': return hex(e)
			elif t == 'bool':
				try: assert isinstance(e, bool)
				except AssertionError: raise Exception, 'Expression "%s" is invalid for type bool.'%str(e)
				return e
			else: raise TypeError, 'Type "%s" not handled'%t
		#########################
		# String Types
		#########################
		elif t in ('string', 'file_open', 'file_save'):
			#do not check if file/directory exists, that is a runtime issue
			e = eval_string(v)
			return str(e)
		#########################
		# Unique ID Type
		#########################
		elif t == 'id':
			#can python use this as a variable?
			try: assert _check_id_matcher.match(v)
			except AssertionError: raise Exception, 'ID "%s" must begin with a letter and may contain letters, numbers, and underscores.'%v
			ids = [param.get_value() for param in self.get_all_params(t)]
			try: assert ids.count(v) <= 1 #id should only appear once, or zero times if block is disabled
			except: raise Exception, 'ID "%s" is not unique.'%v
			try: assert v not in ID_BLACKLIST
			except: raise Exception, 'ID "%s" is blacklisted.'%v
			return v
		#########################
		# Stream ID Type
		#########################
		elif t == 'stream_id':
			#get a list of all stream ids used in the virtual sinks 
			ids = [param.get_value() for param in filter(
				lambda p: p.get_parent().is_virtual_sink(),
				self.get_all_params(t),
			)]
			#check that the virtual sink's stream id is unique
			if self.get_parent().is_virtual_sink():
				try: assert ids.count(v) <= 1 #id should only appear once, or zero times if block is disabled
				except: raise Exception, 'Stream ID "%s" is not unique.'%v
			#check that the virtual source's steam id is found
			if self.get_parent().is_virtual_source():
				try: assert v in ids
				except: raise Exception, 'Stream ID "%s" is not found.'%v
			return v
		#########################
		# Grid Position Type
		#########################
		elif t == 'grid_pos':
			if not v: return '' #allow for empty grid pos
			e = self.get_parent().get_parent().evaluate(v)
			try:
				assert isinstance(e, (list, tuple)) and len(e) == 4
				for ei in e: assert isinstance(ei, int)
			except AssertionError: raise Exception, 'A grid position must be a list of 4 integers.'
			row, col, row_span, col_span = e
			#check row, col
			try: assert row >= 0 and col >= 0
			except AssertionError: raise Exception, 'Row and column must be non-negative.'
			#check row span, col span
			try: assert row_span > 0 and col_span > 0
			except AssertionError: raise Exception, 'Row and column span must be greater than zero.'
			#get hostage cell parent
			try: my_parent = self.get_parent().get_param('notebook').evaluate()
			except: my_parent = ''
			#calculate hostage cells
			for r in range(row_span):
				for c in range(col_span):
					self._hostage_cells.append((my_parent, (row+r, col+c)))
			#avoid collisions
			params = filter(lambda p: p is not self, self.get_all_params('grid_pos'))
			for param in params:
				for parent, cell in param._hostage_cells:
					if (parent, cell) in self._hostage_cells:
						raise Exception, 'Another graphical element is using parent "%s", cell "%s".'%(str(parent), str(cell))
			return e
		#########################
		# Notebook Page Type
		#########################
		elif t == 'notebook':
			if not v: return '' #allow for empty notebook
			#get a list of all notebooks
			notebook_blocks = filter(lambda b: b.get_key() == 'notebook', self.get_parent().get_parent().get_enabled_blocks())
			#check for notebook param syntax
			try: notebook_id, page_index = map(str.strip, v.split(','))
			except: raise Exception, 'Bad notebook page format.'
			#check that the notebook id is valid
			try: notebook_block = filter(lambda b: b.get_id() == notebook_id, notebook_blocks)[0]
			except: raise Exception, 'Notebook id "%s" is not an existing notebook id.'%notebook_id
			#check that page index exists
			try: assert int(page_index) in range(len(notebook_block.get_param('labels').get_evaluated()))
			except: raise Exception, 'Page index "%s" is not a valid index number.'%page_index
			return notebook_id, page_index
		#########################
		# Import Type
		#########################
		elif t == 'import':
			n = dict() #new namespace
			try: exec v in n
			except ImportError: raise Exception, 'Import "%s" failed.'%v
			except Exception: raise Exception, 'Bad import syntax: "%s".'%v
			return filter(lambda k: str(k) != '__builtins__', n.keys())
		#########################
		else: raise TypeError, 'Type "%s" not handled'%t

	def to_code(self):
		"""
		Convert the value to code.
		For string and list types, check the init flag, call evaluate().
		This ensures that evaluate() was called to set the xxxify_flags.
		@return a string representing the code
		"""
		v = self.get_value()
		t = self.get_type()
		if t in ('string', 'file_open', 'file_save'): #string types
			if not self._init: self.evaluate()
			if self._stringify_flag: return '"%s"'%v.replace('"', '\"')
			else: return v
		elif t in ('complex_vector', 'real_vector', 'int_vector'): #vector types
			if not self._init: self.evaluate()
			if self._lisitify_flag: return '(%s, )'%v
			else: return '(%s)'%v
		else: return v

	def get_all_params(self, type):
		"""
		Get all the params from the flowgraph that have the given type.
		@param type the specified type
		@return a list of params
		"""
		return sum([filter(lambda p: p.get_type() == type, block.get_params()) for block in self.get_parent().get_parent().get_enabled_blocks()], [])
