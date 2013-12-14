#!/usr/bin/python3

#  Copyright (C) 2013 Jussi Pakkanen
#
#  Authors:
#     Jussi Pakkanen <jpakkane@gmail.com>
#
#  This library is free software; you can redistribute it and/or modify it under
#  the terms of version 3 of the GNU General Public License as published
#  by the Free Software Foundation.
#
#  This library is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from glob import glob
import os
import subprocess
import re

def barechecker(infile):
    if len(open(infile).read()) > 1024:
        print('Source file', infile, 'too long.')
    src = open(infile).read()
    if '#' in src or '??=' in src:
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
    if len(open(infile).read()) > 512:
        print('Source file', infile, 'too long.')
    includere = re.compile('''^\s*#\s*include\s*[<"](.*?)[>"]''')
    for line in open(infile):
        m = re.search(includere, line)
        if m:
            include = m.group(1)
            if include not in permitted:
                print("Invalid include", include, "in", infile)
                return False
        elif '#' in line or '??=' in line:
            print('Invalid use of preprocessor in', infile)
            return False
    return True

def anythingchecker(infile):
    if len(open(infile).read()) > 256:
        print('Source file', infile, 'too long.')
    return True

def packages_installed(packagefile):
    if not os.path.isfile(packagefile):
        print('Package file missing in ', packagefile)
    for line in open(packagefile).readlines():
        line = line.strip()
        if line == '':
            continue
        cmd = ['aptitude', 'show', line]
        pc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        so = pc.communicate()[0].decode()
        if not 'State: installed' in so:
            print('Package', line, 'not installed in', packagefile)
            return False
    return True

def info_ok(infofile):
    if not os.path.isfile(infofile):
        print('Info file missing for', infofile)
        return False
    lines = open(infofile).readlines()
    if len(lines) != 3:
        print('Incorrect number of lines in info file in', infofile)
        return False
    elems = lines[0].strip().split()
    if len(elems) != 2:
        print('Malformed email line in', infofile)
        return False
    if elems[0] != 'email' or '@' not in elems[1]:
        print('Malformed email line in', infofile)
        return False
    elems = lines[1].strip().split()
    if len(elems) < 2 or elems[0] != 'title':
        print('Malformed title line in', infofile)
        return False
    elems = lines[2].strip().split()
    if len(elems) < 2 or elems[0] != 'author':
        print('Malformed author line in', infofile)
        return False
    return True

def has_extra_files(d, basename):
    allowed = {'info.txt' : True,
               'includes.txt' : True,
               'packages.txt' : True,
               basename + '.cpp' : True}
    for d in glob(os.path.join(d, '*')):
        base = os.path.split(d)[-1]
        if base not in allowed:
            print(d, 'has an extra file', base)

def measure(subdir):
    compiler = '/usr/bin/g++'
    basic_flags = ['-std=c++11', '-fmax-errors=1', '-c', '-o', '/dev/null']
    results = []
    for d in glob(os.path.join(subdir, '*')):
        basename = os.path.split(d)[-1]
        sourcename = basename + '.cpp'
        fullsrc = os.path.join(d, sourcename)
        if has_extra_files(d, basename):
            continue
        if not os.path.isfile(fullsrc):
            print('Missing source file', fullsrc)
            continue
        infofile = os.path.join(d, 'info.txt')
        packagefile = os.path.join(d, 'packages.txt')
        if subdir == 'anything':
            if not packages_installed(packagefile):
                continue
        else:
            if os.path.isfile(packagefile):
                print('Package file exists in non-anything dir', basename)
                continue
        if not info_ok(infofile):
            continue
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
        print('%.2f' % i[0], i[1], i[2], i[3])
    print('')
    print('Starting measurements for type bare hands.')
    bare_times = measure('barehands')
    print('Table for category bare hands:\n')
    for i in bare_times:
        print('%.2f' % i[0], i[1], i[2], i[3])
    print('')
    print('Starting measurements for type anything.')
    anything_times = measure('anything')
    print('Table for category anything:\n')
    for i in anything_times:
        print('%.2f' % i[0], i[1], i[2], i[3])
    print('')

if __name__ == '__main__':
    run()
