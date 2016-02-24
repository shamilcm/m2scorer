#!/usr/bin/python

# Read a  nbest list and then obtain the oracle F0.5 score
# Format of n-best list should be : 
#<sentence_index> ||| <hypothesis sentence> ||| <...ignored sections...>

#from scripts import levenshtein
import scorer.levenshtein
import argparse
import sys
import os
from scorer.reader import load_annotation
from scorer.util import smart_open
from scorer.reader import read_nbest_sentences

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_nbest', dest='input_nbest_path', required=True, help="Path to input nbest file")
parser.add_argument('-m', '--input_m2file',dest='input_m2_path', required=True, help="Path to input m2 file")
parser.add_argument('-o', '--output_dir_path', dest='output_dir_path', default=".", help="Path to output directory")
parser.add_argument('-e', '--error_types', dest='error_types', default='all', help="Comma separated error types" )
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',  help="For verbose output" )
args = parser.parse_args()

filter_etypes=args.error_types.split(',')
source_sentences, gold_edits = load_annotation(args.input_m2_path, filter_etypes)


nbest_sentences = read_nbest_sentences(args.input_nbest_path)
assert len(nbest_sentences) == len(source_sentences) == len(gold_edits)




# M2Scorer Parameters
max_unchanged_words=2
beta = 0.5
ignore_whitespace_casing= False
verbose = False
very_verbose = False


system_sentences = []
index = 0
for nbest,source,golds_set in zip(nbest_sentences,source_sentences, gold_edits):
	best_candidate_score = 0.0
	c_index = 0

	if args.verbose is False:
		print >>sys.stderr, "Sentence Index:" + str(index)
		print >>sys.stderr, "Original:" + source
	
	for candidate in nbest:
		if (args.verbose):
			print >>sys.stderr, "Sentence Index:" + str(index)
			print >>sys.stderr, "Original:" + source
			print >>sys.stderr, "Hypothesis:" + candidate
		score = 0.0
		ann_score = 0.0
		for annotator, gold in golds_set.iteritems():
			p,r,  ann_score = scorer.levenshtein.pre_rec_f1(candidate, source, gold,  max_unchanged_words, beta, ignore_whitespace_casing, verbose, very_verbose )
			if ann_score >= score:
				score = ann_score 
		if c_index == 0:
			best_candidate = candidate
			best_candidate_score = score
		elif score >  best_candidate_score:
			best_candidate = candidate
			best_candidate_score = score
		c_index += 1
		if (args.verbose):
			print >> sys.stderr, "Score", score
	print >> sys.stderr, "Best Candidate: " + best_candidate + "(score=" + str(best_candidate_score) + ")\n"
	index += 1
	system_sentences.append(best_candidate)


if not os.path.exists(args.output_dir_path):
    os.makedirs(args.output_dir_path)
    
f=open(args.output_dir_path+'/'+'output_oracle.txt','wb')
for sentence in system_sentences:
	f.write(sentence.encode("UTF-8")+'\n')
f.close()

p, r, f1 = scorer.levenshtein.batch_multi_pre_rec_f1(system_sentences, source_sentences, gold_edits, max_unchanged_words, beta, ignore_whitespace_casing, verbose, very_verbose)

print "Precision   : %.4f" % p
print "Recall      : %.4f" % r
print "F_%.1f       : %.4f" % (beta, f1)
