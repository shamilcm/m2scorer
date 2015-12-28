#!/usr/bin/python

# This file is part of the NUS M2 scorer.
# The NUS M2 scorer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# The NUS M2 scorer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# file: m2scorer.py
# 
# score a system's output against a gold reference 
#
# Usage: m2scorer.py [OPTIONS] proposed_sentences source_gold
# where
#  proposed_sentences   -   system output, sentence per line
#  source_gold          -   source sentences with gold token edits
# OPTIONS
#   -v    --verbose             -  print verbose output
#   --very_verbose              -  print lots of verbose output
#   --max_unchanged_words N     -  Maximum unchanged words when extracting edits. Default 2."
#   --beta B                    -  Beta value for F-measure. Default 0.5."
#   --ignore_whitespace_casing  -  Ignore edits that only affect whitespace and caseing. Default no."
#   --error_type <ERRORTYPE>	-  Score only one particular error type e.g. ArtorDet, Mec, Wform, Wci
#

import sys
from scorer import levenshtein
from getopt import getopt
from scorer.util import paragraphs
from scorer.util import smart_open
from scorer.reader import load_annotation


def print_usage():
    print >> sys.stderr, "Usage: m2scorer.py [OPTIONS] proposed_sentences gold_source"
    print >> sys.stderr, "where"
    print >> sys.stderr, "  proposed_sentences   -   system output, sentence per line"
    print >> sys.stderr, "  source_gold          -   source sentences with gold token edits"
    print >> sys.stderr, "OPTIONS"
    print >> sys.stderr, "  -v    --verbose                   	-  print verbose output"
    print >> sys.stderr, "        --very_verbose              	-  print lots of verbose output"
    print >> sys.stderr, "        --max_unchanged_words N     	-  Maximum unchanged words when extraction edit. Default 2."
    print >> sys.stderr, "        --beta B                    	-  Beta value for F-measure. Default 0.5."
    print >> sys.stderr, "        --ignore_whitespace_casing  	-  Ignore edits that only affect whitespace and caseing. Default no."
    print >> sys.stderr, "        --error_type ERROR_TYPES	-  Score only for particular error types, Use comma-separated values e.g. Wci or Wci,ArtOrDet, or Prep,NN,ArtOrDet or all"


max_unchanged_words=2
beta = 0.5
ignore_whitespace_casing= False
verbose = False
very_verbose = False
filter_etypes = ["all"]
opts, args = getopt(sys.argv[1:], "v", ["max_unchanged_words=", "beta=", "verbose", "ignore_whitespace_casing", "very_verbose", "error_type="])
for o, v in opts:
    if o in ('-v', '--verbose'):
        verbose = True
    elif o == '--very_verbose':
        very_verbose = True
    elif o == '--max_unchanged_words':
        max_unchanged_words = int(v)
    elif o == '--beta':
        beta = float(v)
    elif o == '--ignore_whitespace_casing':
        ignore_whitespace_casing = True
    elif o == '--error_type':
		filter_etypes = v.split(",")
    else:
        print >> sys.stderr, "Unknown option :", o
        print_usage()
        sys.exit(-1)

# starting point
if len(args) != 2:
    print_usage()
    sys.exit(-1)

system_file = args[0]
gold_file = args[1]

# load source sentences and gold edits
source_sentences, gold_edits = load_annotation(gold_file, filter_etypes)

# load system hypotheses
fin = smart_open(system_file, 'r')
system_sentences = [line.decode("utf8").strip() for line in fin.readlines()]
fin.close()

p, r, f1 = levenshtein.batch_multi_pre_rec_f1(system_sentences, source_sentences, gold_edits, max_unchanged_words, beta, ignore_whitespace_casing, verbose, very_verbose)

print "Precision   : %.4f" % p
print "Recall      : %.4f" % r
print "F_%.1f       : %.4f" % (beta, f1)

