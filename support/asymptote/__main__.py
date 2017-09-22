import sys, os, shutil
from lib import util, make

EXTS = {
    'PDF': '.pdf',
    'SVG': '.svg'
}

FMTS = {y: x for x, y in EXTS.items()}

ASY_FMTS = {
    'PDF': 'pdf',
    'SVG': 'svg',
}

def _asymptote(in_path, out_path, asymptote_dir, working_dir, fmt='pdf'):
    args = [os.environ['ASYMPTOTE'], '-vv', '-f', ASY_FMTS[fmt], '-o', out_path, in_path]
    
    with util.command_context(args, set_env={'ASYMPTOTE_DIR': asymptote_dir}, working_dir=working_dir, use_stderr=True) as process:
        def get_loaded_file(line):
            if any(line.startswith(j) for j in ['Loading ', 'Including ']):
                parts = line.rstrip('\n').split(' ')
                
                if len(parts) == 4:
                    _, _, from_, path = parts
                    
                    if from_ == 'from':
                        return path
            
            return None
        
        def iter_loaded_files():
            for i in process.stderr:
                loaded_file = get_loaded_file(i)
                
                if loaded_file is not None:
                    yield loaded_file
                elif not any(i.startswith(j) for j in ['cd ', 'Using configuration ']):
                    print >> sys.stderr, i,
        
        loaded_files = list(iter_loaded_files())
    
    return loaded_files


@util.main
def main(in_path, out_path, asymptote_dir, save_dependencies=True):

    if isinstance(save_dependencies, (str, unicode)):
        save_dependencies = True if save_dependencies == 'True' else False

    try:
        _, out_suffix = os.path.splitext(out_path)

        fmt = FMTS[out_suffix]
        
        with util.TemporaryDirectory() as temp_dir:
            absolute_in_path = os.path.abspath(in_path)
            temp_out_path = os.path.join(temp_dir, 'out{format_ext}'.format(format_ext=EXTS[fmt]))

            # Asymptote creates A LOT of temp files (presumably when invoking
            #  LaTeX) and leaves some of them behind. Thus we run asymptote
            # in a temporary directory.
            loaded_files = _asymptote(
                absolute_in_path,
                'out',
                os.path.abspath(asymptote_dir),
                temp_dir,
                fmt=fmt)
            
            if not os.path.exists(temp_out_path):
                print("[ERROR] temp_out_path: " + temp_out_path)
                print(os.listdir(temp_dir))
                raise util.UserError('Asymptote did not generate a {fmt} file.'.format(fmt=fmt), in_path)
            
            if save_dependencies:
                # All dependencies as paths relative to the project root.
                dependencies = set(map(os.path.relpath, loaded_files))
                
                # Write output files.
                d, f = os.path.dirname(out_path), os.path.basename(out_path)
                make.write_dependencies(
                    os.path.join(d, '.{}.d'.format(f)), 
                    out_path, 
                    dependencies - {in_path})

            shutil.copyfile(temp_out_path, out_path)

    except util.UserError as e:
        raise util.UserError('While processing {}: {}', in_path, e)


if __name__ == "__main__":
    main(*sys.argv[1:])
