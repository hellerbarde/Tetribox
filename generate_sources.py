#! /usr/bin/env python3
import os
import sys
import argparse


class Piece(object):
    def get_asy_code(self, piece_type, arguments):
        return ("import _{piece_type};\n"
        "{piece_type}({arguments});\n").format(
            piece_type=piece_type,
            arguments=', '.join(str(x) for x in arguments))
    
    def get_file_name(self):
        NotImplemented

    @staticmethod
    def side_variants(variant_name):
        return {
            'a': 0,
            'b': 1
        }[variant_name]

    def __repr__(self):
        return self.get_file_name()


class Divider(Piece):
    def __init__(self, size):
        self.size = size

    def get_asy_code(self):
        return super().get_asy_code("divider", [self.size])

    def get_file_name(self):
        return f"divider-{self.size}.asy"


class Side(Piece):
    def __init__(self, size, variant, has_holes):
        self.size = size
        if size % 2:
            # odd
            assert variant == 'a', "if the size is odd, only variant 'a' is valid."
        self.variant = variant
        self.has_holes = has_holes
    
    def get_asy_code(self):
        side_variants = {
            'a': 0,
            'b': 1
        }
        return super().get_asy_code("side", [
            self.size, 
            super().side_variants(self.variant), 
            'true' if self.has_holes else 'false'])
    
    def get_file_name(self):
        filename = f"side-{self.size}"
        
        if not self.size % 2:
            # even
            filename += f"-{self.variant}"
        if self.has_holes:
            filename += "-holes"

        return filename + ".asy"


class Base(Piece):
    def __init__(self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey

    def get_asy_code(self):
        return super().get_asy_code("base", [self.sizex, self.sizey])

    def get_file_name(self):
        return f"base-{self.sizex}-{self.sizey}.asy"


def generate_file(full_path):
    dirname = os.path.dirname(full_path)
    basename = os.path.basename(full_path)
    
    piece = deconstruct_filename(basename)
    
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(full_path, 'w') as fd:
        fd.write(piece.get_asy_code())


def output_filenames(directory=''):
    pieces = generate_pieces()
    for piece in pieces:
        print(os.path.join(directory, piece.get_file_name()))


def generate_pieces():
    all_pieces = []
    for i in range(1, 15):
        all_pieces.append(Divider(size=i))

        if not i % 2:
            #number is even
            # Without holes
            all_pieces.append(Side(size=i, variant='a', has_holes=False))
            all_pieces.append(Side(size=i, variant='b', has_holes=False))
            # With holes
            all_pieces.append(Side(size=i, variant='a', has_holes=True))
            all_pieces.append(Side(size=i, variant='b', has_holes=True))
        else:
            #number is odd
            # Without holes
            all_pieces.append(Side(size=i, variant='a', has_holes=False))
            # With holes
            all_pieces.append(Side(size=i, variant='a', has_holes=True))
        
        for j in range(1, 12):
            if j <= i:
                all_pieces.append(Base(sizex=i, sizey=j))
    return all_pieces

def deconstruct_filename(filename):
    """Exists for legacy reasons, to keep compatibility with the Makefile"""

    parts = filename.split('.')[0].split('-')

    if parts[0] == 'base':
        return Base(sizex=int(parts[1]), sizey=int(parts[2]))
    if parts[0] == 'divider':
        return Divider(size=int(parts[1]))
    if parts[0] == 'side':
        has_holes = parts[-1] == 'holes'

        if (int(parts[1]) % 2) == 0:
            #even
            return Side(size=int(parts[1]), variant=parts[2], has_holes=has_holes)
        else:
            #odd
            return Side(size=int(parts[1]), variant='a', has_holes=has_holes)


if __name__ == '__main__':

    # parser = argparse.ArgumentParser(prog='PROG')
    # parser.add_argument('--foo', action='store_true', help='foo help')
    # subparsers = parser.add_subparsers(help='sub-command help')

    # # create the parser for the "a" command
    # parser_a = subparsers.add_parser('a', help='a help')
    # parser_a.add_argument('bar', type=int, help='bar help')

    # # create the parser for the "b" command
    # parser_b = subparsers.add_parser('b', help='b help')
    # parser_b.add_argument('--baz', choices='XYZ', help='baz help')

    # # parse some argument lists
    # parser.parse_args(['a', '12'])

    # parser.parse_args(['--foo', 'b', '--baz', 'Z'])

    parser = argparse.ArgumentParser(description='Generate Tetribox Asymptote Files')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    
    parser_list_files = subparsers.add_parser('list', help='list all files to be generated (for the makefile)')
    parser_list_files.add_argument('-d', '--dir', default="./src", dest='directory',
                                   help='directory in which to generate the files.')
    
    parser_generate = subparsers.add_parser('generate', help='generate files')
    parser_generate.add_argument('file', type=str, nargs='+',
                                 help='list of files to be generated')
    
    parser_build = subparsers.add_parser('build', help='build files')
    parser_build.add_argument('-t', '--type', default='pdf', dest='build_type', 
                              choices=['pdf', 'svg'],
                              help='type of file to build')
    parser_build.add_argument('build_file', type=str, nargs='+',
                              help='list of files to be built')
    
    args = parser.parse_args()

    if args.subcommand == 'list':
        output_filenames(directory=args.directory)

    elif args.subcommand == 'generate':
        for f in args.file:
            generate_file(f)

    # else:
    #     parser.print_help()
    #     # print("whelp, this shouldn't happen... But it did.")
