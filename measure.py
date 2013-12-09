#!/usr/bin/python3

from glob import glob
import os
import subprocess
import re

def plainchecker(infile):
    permitted = {'vector' : True,
                 'map' : True,
                 'iostream' : True,
                 }
    includere = re.compile('''^\s*#\s*include\s*[<"](.*?)[>"]''')
    for line in open(infile):
        if '#define' in line:
            print("Invalid use of preprocessor detected in", infile)
            return False
        m = re.search(includere, line)
        if m:
            include = m.group(1)
            if include not in permitted:
                print("Invalid include", include, "in", infile)
                return False
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
        if not checker(fullsrc):
            continue
        if not os.path.isfile(fullsrc):
            print("Bad file in subdir", d)
            continue
        cmd = [compiler, fullsrc] + basic_flags
        pc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = pc.communicate()
        stdout = res[1]
        num_chars = len(open(fullsrc).read())
        num_lines = len(stdout.split(b'\n'))
        if num_lines == 0:
            print('Empty input file in subdir', d)
            continue
        ratio = num_lines / num_chars
        results.append((ratio, num_chars, num_lines, basename))
    results.sort(reverse=True)
    return results

def run():
    print('Starting measurements for type plain')
    plain_times = measure('plain')
    print('Table for category plain:\n')
    for i in plain_times:
        print(i[0], i[1], i[2], i[3])

if __name__ == '__main__':
    run()
