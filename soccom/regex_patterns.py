# This file contains whatever pattern things we are trying to extract from each module
import re

# pat_io_v = r'(input|output|inout|reg)\s+([^;]+);'
pat_io_v = r'(input|output|inout|reg)\s+([-\'\w`\[:\].,*={} ]+)'
# pat_io_sv = r'(input|output|inout|reg)\s+([^;]+);'
pat_io_sv = r'(input|output|inout|reg)\s+([-\'\w`\[:\].,*={} ]+)'
pat_module = r'\s*module\s+(\w+)\b'
pat_line_comment = r'//.*'
pat_block_comment = r'/[*]((.|\n)*?)[*]/'
pat_param = r'(parameter|localparam)\s+([-\'\w`\[:\].,;*={} ]+)'
pat_packages = r'import\s+(\w+)::((?:\w|[*]|,)+);'
pat_includes = r'`include\s+["]([A-Za-z0-9_./]+)["]'

re_pat_io_v = re.compile(pat_io_v)
re_pat_io_sv = re.compile(pat_io_sv)
re_pat_module = re.compile(pat_module)
re_pat_line_comment = re.compile(pat_line_comment)
re_pat_block_comment = re.compile(pat_block_comment)
re_pat_param = re.compile(pat_param)
re_pat_packages = re.compile(pat_packages)
re_pat_includes = re.compile(pat_includes)
