#!/usr/bin/python

# Read a moses nbest list and then obtain the oracle F0.5 score

#from scripts import levenshtein
import scorer.levenshtein
import argparse
import sys
from scripts.reader import load_annotation
from scripts.util import smart_open
from scripts.reader import read_nbest_sentences

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_nbest', dest='input_nbest_path', required=True, help="Path to input nbest file")
parser.add_argument('-m', '--input_m2file',dest='input_m2_path', required=True, help="Path to input m2 file")
parser.add_argument('-o', '--output_dir_path', dest='output_dir_path', help="Path to output directory")
parser.add_argument('-e', '--error_types', dest='error_types', default='all', help="Comma separated error types" )
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
	for candidate in nbest:
		print >>sys.stderr, "Sentence Index:" + str(index)
		print >>sys.stderr, "Source:" + source
		print >>sys.stderr, "Hypothesis:" + candidate
		score = 0.0
		ann_score = 0.0
		for annotator, gold in golds_set.iteritems():
			p,r,  ann_score = scripts.levenshtein.pre_rec_f1(candidate, source, gold,  max_unchanged_words, beta, ignore_whitespace_casing, verbose, very_verbose )
			if ann_score >= score:
				score = ann_score 
		if c_index == 0:
			best_candidate = candidate
			best_candidate_score = score
		elif score >  best_candidate_score:
			best_candidate = candidate
			best_candidate_score = score
		c_index += 1
		print >> sys.stderr, "Score", score
	print >> sys.stderr, "best: " + best_candidate + "(score=" + str(best_candidate_score) + ")\n"
	index += 1
	system_sentences.append(best_candidate)

f=open('output_oracle.txt','wb')
for sentence in system_sentences:
	f.write(sentence.encode("UTF-8")+'\n')
f.close()

#p, r, f1 = scripts.levenshtein.batch_multi_pre_rec_f1(system_sentences, source_sentences, gold_edits, max_unchanged_words, beta, ignore_whitespace_casing, verbose, very_verbose)

#print "Precision   : %.4f" % p
#print "Recall      : %.4f" % r
#print "F_%.1f       : %.4f" % (beta, f1)
