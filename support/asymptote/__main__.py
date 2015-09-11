import os, shutil
from lib import util


def _asymptote(in_path, out_path, asymptote_dir, working_dir):
	util.command([os.environ['ASYMPTOTE'], '-f', 'pdf', '-o', out_path, in_path], set_env = { 'ASYMPTOTE_DIR': asymptote_dir }, working_dir = working_dir)


@util.main
def main(in_path, out_path):
	_, out_suffix = os.path.splitext(out_path)
	
	if out_suffix == '.pdf':
		with util.TemporaryDirectory() as temp_dir:
			absolute_in_path = os.path.abspath(in_path)
			temp_out_path = os.path.join(temp_dir, 'out.pdf')
			
			# Asymptote creates A LOT of temp files (presumably when invoking LaTeX) and leaves some of them behind. Thus we run asymptote in a temporary directory.
			_asymptote(absolute_in_path, 'out', os.path.dirname(absolute_in_path), temp_dir)
			
			if not os.path.exists(temp_out_path):
				raise util.UserError('Asymptote did not generate a PDF file for input file {}.', in_path)
			
			shutil.copyfile(temp_out_path, out_path)
	else:
		raise Exception('Unknown file type: {}'.format(out_suffix))
