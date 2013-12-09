#!/usr/bin/python3

from glob import glob
import os
import subprocess
import re

def barechecker(infile):
    if '#' in open(infile).read():
        print("Attempt to use the preprocessor in", infile)
        return False
    return True

def plainchecker(infile):
    permitted = {'vector' : True,
                 'map' : True,
                 'iostream' : True,
                 'functional' : True,
                 'memory' : True,
                 'utility' : True,
                 'stdexcept' : True,
                 'string' : True,
                 'set' : True,
                 'unordered_map' : True,
                 'unordered_set' : True,
                 'regex' : True,
                 'array' : True,
                 'stack' : True,
                 'queue' : True,
                 'algorithm' : True,
                 'iterator' : True,
                 'complex' : True,
                 'atomic' : True,
                 'thread' : True,
                 'mutex' : True,
                 'future' : True,
                 'typeinfo' : True,
                 'tuple' : True,
                 'initializer_list' : True
                 }
    includere = re.compile('''^\s*#\s*include\s*[<"](.*?)[>"]''')
    for line in open(infile):
        m = re.search(includere, line)
        if m:
            include = m.group(1)
            if include not in permitted:
                print("Invalid include", include, "in", infile)
                return False
        elif '#' in line:
            print('Invalid use of preprocessor in', infile)
            return False
    return True

def anythingchecker(infile):
    return True

def measure(subdir):
    compiler = '/usr/bin/g++'
    basic_flags = ['-std=c++11', '-c', '-o', '/dev/null']
    results = []
    for d in glob(os.path.join(subdir, '*')):
        basename = os.path.split(d)[-1]
        sourcename = basename + '.cpp'
        fullsrc = os.path.join(d, sourcename)
        if subdir == 'plain':
            checker = plainchecker
        elif subdir == 'barehands':
            checker = barechecker
        else:
            checker = anythingchecker
        if not checker(fullsrc):
            continue
        if not os.path.isfile(fullsrc):
            print("Bad file in subdir", d)
            continue
        cmd = [compiler, fullsrc] + basic_flags
        if subdir == 'anything':
            includefile = os.path.join(d, 'includes.txt')
            for line in open(includefile):
                cmd.append('-I' + line.strip())
        pc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = pc.communicate()
        stderr = res[1]
        input_size = len(open(fullsrc).read())
        output_size = len(stderr)
        if output_size == 0:
            print('Empty input file in subdir', d)
            continue
        ratio = output_size / input_size
        results.append((ratio, input_size, output_size, basename))
    results.sort(reverse=True)
    return results

def run():
    print('Starting measurements for type plain.')
    plain_times = measure('plain')
    print('Table for category plain:\n')
    for i in plain_times:
        print(i[0], i[1], i[2], i[3])
    print('')
    print('Starting measurements for type bare hands.')
    bare_times = measure('barehands')
    print('Table for category bare hands:\n')
    for i in bare_times:
        print(i[0], i[1], i[2], i[3])
    print('')
    print('Starting measurements for type anything.')
    anything_times = measure('anything')
    print('Table for category anything:\n')
    for i in anything_times:
        print(i[0], i[1], i[2], i[3])
    print('')

if __name__ == '__main__':
    run()
