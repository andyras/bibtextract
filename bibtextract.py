#!/usr/bin/env python2.7

################################################################################
#                                                                              #
#     bibtextract: condense a bibtex library to fit latex citations            #
#     Copyright (C) 2013 Andrew M. Rasmussen                                   #
#     Please send bug reports, etc., to andyras@gmail.com                      #
#                                                                              #
#     This program is free software: you can redistribute it and/or modify     #
#     it under the terms of the GNU General Public License as published by     #
#     the Free Software Foundation, either version 3 of the License, or        #
#     (at your option) any later version.                                      #
#                                                                              #
#     This program is distributed in the hope that it will be useful,          #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#     GNU General Public License for more details.                             #
#                                                                              #
#     You should have received a copy of the GNU General Public License        #
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                              #
################################################################################

#### parse arguments

import argparse

parser = argparse.ArgumentParser(description='This script extracts the bibtex citation keys from a .bib file which are used in a .tex file, and creates a new, minimal .bib file containing only those keys.')
parser.add_argument('bibFile', help='.bib library to be parsed', type=str, metavar='<bibtex library>')
parser.add_argument('texFile', help='.tex file to be parsed', type=str, metavar='<tex file>')
parser.add_argument('newBibFile', help='minimal .bib library to be created', type=str, metavar='<new library>')
parser.add_argument('-d', '--debug', help='turn on debug output', action='store_true', default=False)

args = parser.parse_args()

debug = args.debug

# error checking
if (args.bibFile == args.newBibFile):
    print 'ERROR: please give different filenames for old and new .bib files'
    exit()

#### parse .bib file

idx = 0     # character index for reading in files
pc = 0      # parenthesis nesting counter
key = ''    # bibtex citation key
entry = ''  # bibtex entry
keys = {}   # map of bibtex citation keys to entries

with open(args.bibFile, 'r') as bib:
    if (debug):
        print '%d starting' % idx
    chars = bib.read()
    while (idx < len(chars)):
        # new key
        if (chars[idx] == '@'):
            if (debug):
                print '%d found new key' % idx
            # find the citation key
            while (chars[idx] != '{'):
                # skip specification of kind of publication
                entry += chars[idx]
                idx += 1
            if (debug):
                print '%d found open paren' % idx
            pc = pc + 1     # we found the first paren for the bibtex entry
            entry += chars[idx] # add paren to entry
            idx += 1
            while (chars[idx] != ','):
                # add characters to the key
                key += chars[idx]
                entry += chars[idx]
                idx += 1
            if (debug):
                print '%d found key end comma' % idx
            entry += chars[idx]
            idx += 1

            # find the remainder of the bibtex entry
            while (pc > 0):
                if (chars[idx] == '{'):
                    pc += 1
                if (chars[idx] == '}'):
                    pc -= 1
                entry += chars[idx]
                idx += 1
            if (debug):
                print '%d finished reading entry' % idx
            #idx += 1

            # now we have the entire entry

            # add key and entry to dict
            key = key.strip()   # there generally won't be whitespace in \cite commands
            if (debug):
                if (key in keys):
                    print 'duplicate key: %s' % key
            keys[key] = entry
            if (debug):
                print 'key is %s' % key
                #print 'entry is %s' % entry

        # done parsing key; reset key and entry strings
        key = ''
        entry = ''
        idx += 1

#### parse .tex file

idx = 6         # character index
cite = ''       # citation
cites = set([]) # set of citations

with open(args.texFile, 'r') as tex:
    chars = tex.read()
    while (idx < len(chars)):
        if ((chars[idx-6:idx] == '\cite{') or (chars[idx-12:idx] == '\onlinecite{')):
            if (debug):
                print '%d \cite command' % idx

            # parse until end of \cite command
            while (chars[idx] != '}'):
                # at comma, add citation to list, reset
                if (chars[idx] == ','):
                    if (debug):
                        print '%d citation "%s"' % (idx, cite)

                    cites.add(cite.strip())
                    cite = ''
                else:
                    cite += chars[idx]

                idx += 1

            # at end of \cite command, add citation to list, reset
            cites.add(cite.strip())
            cite = ''
            if (debug):
                print '%d citation "%s"' % (idx, cite)
                print '%d done parsing \cite command' % idx

        idx += 1

#### write new .bib file

with open(args.newBibFile, 'w') as newBib:
    for cite in cites:
        if (debug):
            print 'writing citation key %s' % cite
        try:
            newBib.write('%s\n' % keys[cite])
        except KeyError:
            print '%s did not write properly' % cite

if (debug):
    print '%d keys found in .bib file' % len(keys.keys())
    print '%d citations in .tex file' % len(cites)
