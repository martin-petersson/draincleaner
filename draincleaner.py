#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import pathspec # use this for git style ignore
import sys
import os
import shutil
import re

metadatastore = '.draincleaner'
metadatafile = 'draincleaner.json'
ignorefile = '.ignorecomments'


def import_file(file):
	openfile = open(file, "r")
	openfile = openfile.read()
	return openfile

import tokenize
from io import StringIO

def remove_special_comment_lines(path, prefix="# ¤"):
	
	# Read file with proper encoding
	with tokenize.open(path) as f:
		code = f.read()
	
	lines = code.splitlines(keepends=True)

	tokens = list(tokenize.generate_tokens(iter(lines).__next__))
	lines_to_skip = set()
	comment_positions = []

	# Detect lines that are ONLY the prefixed comment
	for tok in tokens:
		if tok.type == tokenize.COMMENT and tok.string.startswith(prefix):
			start_line, start_col = tok.start
			end_line, end_col = tok.end
			line_text = lines[start_line - 1]
			if line_text[:start_col].strip() == "":  # nothing before comment
				lines_to_skip.add(start_line)
			else:
				comment_positions.append((start_line, start_col, end_col))

	# Remove trailing prefixed comments from code
	new_lines = []
	for i, line in enumerate(lines, start=1):
		if i in lines_to_skip:
			continue  # remove whole line
		# Remove trailing prefixed comment if it exists
		for start_line, start_col, end_col in comment_positions:
			if start_line == i:
				line = line[:start_col].rstrip() + "\n"
		new_lines.append(line)

	# Write back to file
	return "".join(new_lines)

def find_print_statements(filepath):
	"""
	Scans a Python source file and returns all print() statements
	along with their line numbers.
	
	Args:
		filepath: Path to the Python source file.
	
	Returns:
		A list of PrintStatement named tuples with line_number and source_line.
	"""
	results = []
	
	with open(filepath, "rb") as f:
		tokens = list(tokenize.tokenize(f.readline))
	
	for i, tok in enumerate(tokens):
		# Look for NAME tokens with value "print"
		if tok.type == tokenize.NAME and tok.string == "print":
			# Confirm it's followed by an OP token "(" (i.e., a call, not a variable named print)
			next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
			if next_tok and next_tok.type == tokenize.OP and next_tok.string == "(":
				line_number = tok.start[0]
				source_line = tok.line.strip()
				# results.append(PrintStatement(line_number, source_line))
				results.append((line_number, source_line))
	
	return results

def find_strings(filepath):
	"""
	Scans a Python source file and returns all string literals
	along with their line numbers.

	Args:
		filepath: Path to the Python source file.

	Returns:
		A list of tuples with (line_number, string_value).
	"""
	results = []

	with open(filepath, "rb") as f:
		tokens = list(tokenize.tokenize(f.readline))

	for tok in tokens:
		if tok.type == tokenize.STRING:
			line_number = tok.start[0]
			string_value = tok.string
			results.append((line_number, string_value))

	return results

def strip_ansi(text):
	return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

def main(args):

	python_normal = '# '
	python_prefix = '# ¤'

	sourcepath = Path(args.sourcepath)
	targetpath = Path(args.targetpath)

	pathobjects = sourcepath.glob('**/*', recurse_symlinks=args.follow_symlinks)
	
	for item in pathobjects:
	
		sourcepath_relative = item.relative_to(sourcepath)
		target = targetpath.joinpath(sourcepath_relative)
		
		if any(part in metadatastore for part in item.parts) == False:
			
			if (spec.match_file(sourcepath_relative) == False):
				
				if item.is_dir(follow_symlinks=args.follow_symlinks) == True:
					
					if target.exists() == False:
						if args.verbose:

							output_gendir = f'{target} does not exist, creating...'
							
							if args.colored != True:
								print(strip_ansi(output_gendir))
							else:
								print(output_gendir)

						if args.dry_run != True:
							
							os.makedirs(target, exist_ok=True)
						
				if item.is_file() == True: # item is a file
					
					if (item.suffix != '.py') and (item.suffix != '.md'):

						if args.replace_all != True:
							
							if str(sourcepath_relative) in modified_files:	
								shutil.copy2(item.resolve(), target, follow_symlinks=args.follow_symlinks)
								print(item.resolve())

								if args.verbose:

									output_copy = f'{green}Copying{reset} {item.name}  =>  {target}{reset}'
									
									if args.colored != True:

										print(strip_ansi(output_copy))

									else:
										print(output_copy)
						else:

							if args.verbose:

								output_copy = f'{green}Copying {item.name}  =>  {target}{reset}'									
								
								if args.colored != True:

									print(strip_ansi(output_copy))

								else:

									print(output_copy)

							shutil.copy2(item.resolve(), target, follow_symlinks=args.follow_symlinks)


					elif item.suffix == '.py':

						if args.replace_all != True:
							
							if str(sourcepath_relative) in modified_files: # check if new/modified

								if args.remove_all == True:
									finalform = remove_special_comment_lines(item, prefix=python_normal)
								
								if args.remove_all == False:
									finalform = remove_special_comment_lines(item, prefix=python_prefix)

								if args.dry_run != True:

									with open(target, "w", encoding="utf-8") as f:
										f.writelines(''.join(finalform))

								else:
									pass

								if args.verbose:
									output_writing = f'{white}Writing {item.name}  =>  {target}{reset}'
									
									if args.colored != True:

										print(strip_ansi(output_writing))

									else:
										print(output_writing)

						else:

							# Remove all comments
							if args.remove_all == True:
								finalform = remove_special_comment_lines(item, prefix=python_normal)
								
								if args.verbose:
									
									output_commentremoval = f'{red}Removing all comments from {item.name}  => {item}{reset}'

									if args.colored != True:
										print(strip_ansi(output_commentremoval))
									else:
										print(output_commentremoval)

							if args.remove_all == False:

								finalform = remove_special_comment_lines(item, prefix=python_prefix)

								if args.verbose:
									
									output_prefixremoval = f'{red}Removing prefixed comments from {item.name}  => {item}{reset}'
									
									if args.colored != True:
										print(strip_ansi(output_prefixremoval))
									
									else:
										print(output_prefixremoval)
							
							if args.dry_run != True:

								with open(target, "w", encoding="utf-8") as f:
									f.writelines(''.join(finalform))

							else:
								pass

							if args.verbose:

									output_writing = f'{white}Writing {item.name}  =>  {target}{reset}'
									
									if args.colored != True:

										print(strip_ansi(output_writing))

									else:
										print(output_writing)

						if args.show_prints:
							printlines = find_print_statements(item)
							
							if printlines != []:
								
								outputpath = f'\n{yellow}print statements in {item}:{reset}\n'

								if args.colored != True:

									print(strip_ansi(outputpath))

								else:
									print(outputpath)

								lastprint = printlines[-1:]
								lastline = lastprint[0][0]
								places = len(str(lastline))

								for line in printlines:

									numplaces = len(str(line[0]))
									zeros = places - numplaces

									linespacing = ' '
									
									for p in range(zeros):
										linespacing += ' '

									outputprint = f'{orange}{linespacing + str(line[0])}:{reset} {blue}{line[1]}{reset}'

									if args.colored != True:

										print(strip_ansi(outputprint))

									else:
										print(outputprint)

								print('')

						if args.show_strings:

							stringlines = find_strings(item)
							
							if stringlines != []:

								outputpath = f'\n{yellow}Strings in {item}:{reset}\n'

								if args.colored != True:
									print(strip_ansi(outputpath))

								else:

									print(outputpath)

								laststring = stringlines[-1:]
								lastline = laststring[0][0]
								places = len(str(lastline))

								for line in stringlines:

									numplaces = len(str(line[0]))
									zeros = places - numplaces

									linespacing = ' '
									
									for p in range(zeros):
										linespacing += ' '


									outputstring = f'{orange}{linespacing + str(line[0])}:{reset} {blue}{line[1]}{reset}'

									if args.colored != True:
										print(strip_ansi(outputstring))
									else:
										print(outputstring)

								print('')

					
					if item.suffix == '.md':
						
						if args.replace_all != True:

							
							if str(sourcepath_relative) in modified_files: # check if new/modified

								markdownstring = import_file(item)
								
								if args.remove_all != True:
									
									# remove comments with prefix
									finalform = re.sub(r'<!--¤.*?-->', '', markdownstring, flags=re.DOTALL)
								
								else:

									# Remove all HTML comments, including multiline ones
									finalform = re.sub(r'<!--.*?-->', '', markdownstring, flags=re.DOTALL)

								if args.dry_run != True:

									with open(target, "w", encoding="utf-8") as f:
										f.writelines(''.join(finalform))
								else:
									pass

								if args.verbose:

									output_writing = f'{white}Writing {item.name}  =>  {target}{reset}'
									
									if args.colored != True:
										print(strip_ansi(output_writing))
									else:
										print(output_writing)
						else:

							markdownstring = import_file(item)
						
							if args.remove_all != True:

								finalform = re.sub(r'<!--¤.*?-->', '', markdownstring, flags=re.DOTALL)
							
							else:
								
								finalform = re.sub(r'<!--.*?-->', '', markdownstring, flags=re.DOTALL)

							if args.dry_run != True:
								
								with open(target, "w", encoding="utf-8") as f:
									f.writelines(''.join(finalform))
							
							else:
								pass

							if args.verbose:
								
								output_writing = f'{white}Writing {item.name}  =>  {target}{reset}'
								
								if args.colored != True:
									
									print(strip_ansi(output_writing))
								
								else:

									print(output_writing)


from random import choice
from info import logo, pink, green, yellow, red, orange, blue, white, reset, randomcolor

colors = [pink, green, yellow, red, orange, blue, white]

def randomcolor(colorlist):
	return choice(colorlist)


title = f'draincleaner - Source file comment removal utility\n{logo}\n'

description_list = [
	f'{randomcolor(colors)}Will ignore paths specified in file named ".ignorecomments" in source path.\n', 
	f'A directory ".draincleaner" is created in the source directory containing metadata.\n\n\n',
	f'draincleaner can run without arguments, when doing so in the root path it will use the same source and target path as last run.\n\n\n{reset}'
]

description_string = ''.join(description_list)

parser = ArgumentParser(prog=title, description=description_string)

parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
parser.add_argument('-c', '--colored', action='store_true', help='Show colored output text')
parser.add_argument('-d', '--dry-run', action='store_true', help='Run utility without actually making any changes')
parser.add_argument('-r', '--remove-all', action='store_true', help='Remove all comments')
parser.add_argument('-a', '--replace-all', action='store_true', help='Replace everything in target path')

parser.add_argument('-p', '--show-prints', action='store_true', help='List all print statements')
parser.add_argument('-s', '--show-strings', action='store_true', help='List all strings')

parser.add_argument('-f', '--follow-symlinks', action='store_true', help='Walk symlinked paths')

parser.add_argument('sourcepath', type=Path)
parser.add_argument('targetpath', type=Path)


import json

def load_metadata():

	if metadatapath.exists():
		
		with open(metadata_filepath, "r") as f:
			return json.load(f)

	else:
		return {"files": {}}

def save_metadata(data):

	if metadatapath.exists() == False:

		if arguments.verbose == True:
			
			output_initmetadata = f'Initialize metadata storage: {metadatapath}'

			if arguments.colored != True:

				print(strip_ansi(output_initmetadata))
			
			else:
				print(output_initmetadata)

		os.makedirs(metadatapath, exist_ok=False)
	
	with metadata_filepath.open('w') as f:
		
		json.dump(data, f, indent=4)

def build_snapshot(source_root):

	snapshot = {}

	for path in source_root.rglob('*', recurse_symlinks=arguments.follow_symlinks):

		if path.is_file() and (metadatastore not in path.parts) and (ignorefile not in path.parts):

			sourcepath_relative = path.relative_to(source_root)
			
			if (spec.match_file(sourcepath_relative) == False):
				
				
				rel = path.relative_to(sourcepath).as_posix()
				stat = path.stat()
				snapshot[rel] = {
					"mtime_ns": stat.st_mtime_ns,
					"size": stat.st_size
				}

	return snapshot



if len(sys.argv) == 1:
	
	parser.print_help()

else:
	
	arguments = parser.parse_args()

	sourcepath = Path(arguments.sourcepath)
	targetpath = Path(arguments.targetpath)

	path_ignorefile = sourcepath.joinpath(ignorefile)
	spec = pathspec.PathSpec.from_lines(
		"gitwildmatch",
		path_ignorefile.read_text().splitlines()
	)
	
	metadata = {}
	metadatapath = sourcepath.joinpath(metadatastore)
	metadata_filepath = metadatapath.joinpath(metadatafile)

	
	metadata = load_metadata()
	
	old_files = metadata.get('files', {})
	new_files = build_snapshot(sourcepath)

	modified_files = set()

	for rel, info in new_files.items():

		old_file = old_files.get(rel)

		# new file
		if old_files.get(rel) == None:

			output_new = f'{green}NEW FILE: {Path(rel).name} in {rel}{reset}'
			
			if arguments.colored != True:
				print(strip_ansi(output_new))
			else:
				print(output_new)

			modified_files.add(rel)
		
		else:
			
			# modified file
			if info['mtime_ns'] != old_file['mtime_ns']:

				output_modified = f'{yellow}MODIFIED: {Path(rel).name} in {rel}{reset}'

				if arguments.colored != True:
					print(strip_ansi(output_modified))
				else:	
					print(output_modified)
				
				modified_files.add(rel)

	# check removed paths
	for item in old_files:
		if item not in new_files:


			output_removed = f'{red}REMOVED: {Path(item).name} in {item}{reset}'

			if arguments.colored != True:
				print(strip_ansi(output_removed))
			else:
				print(output_removed)


	metadata['files'] = new_files
	
	if arguments.dry_run != True:
		save_metadata(metadata)
	
	main(arguments)


