# -*- coding: utf-8 -*-
import sys
import getopt
import re


## begin longest common subseuence
sys.setrecursionlimit(100000)

def memoize(fn):
  '''Return a memoized version of the input function.
  
  The returned function caches the results of previous calls.
  Useful if a function call is expensive, and the function 
  is called repeatedly with the same arguments.
  '''
  cache = dict()
  def wrapped(*v):
    key = tuple(v) # tuples are hashable, and can be used as dict keys
    if key not in cache:
      cache[key] = fn(*v)
    return cache[key]
  return wrapped

def LCS(xs, ys):
  '''Return the longest subsequence common to xs and ys.
  Example
  >>> lcs("HUMAN", "CHIMPANZEE")
  ['H', 'M', 'A', 'N']
  '''
  @memoize
  def lcs_(i, j):
    if i and j:
      # print type(i), type(j)
      xe, ye = xs[i-1], ys[j-1]
      # print xe[0], ye
      if xe[0] == ye[0]:
        return lcs_(i-1, j-1) + [(xe[0], (xe[1], ye[1]))]
      else:
        return max(lcs_(i, j-1), lcs_(i-1, j), key=len)
    else:
      return []
  return lcs_(len(xs), len(ys))

## end longest common subseuence


## Labeling characters in s_ori with segmentation {B,M,E,S} labels;
def label_BMES(sequence):
  sequence = sequence.replace('UNK', '€')
  words_list = sequence.split()
  labeled_words_list = []
  label_list = []
  for w in words_list:
    ch_list = ' '.join(w.decode('utf8')).encode('utf8').split()
    if len(ch_list) == 1:
      labeled_words_list.append((ch_list[0], 's'))
      label_list.append('s')
      continue
    for i in range(len(ch_list)):
      if i == 0:
        labeled_words_list.append((ch_list[i], 'b'))
        label_list.append('b')
      elif i == len(ch_list)-1:
        labeled_words_list.append((ch_list[i], 'e'))
        label_list.append('e')
      else:
        labeled_words_list.append((ch_list[i], 'm'))
        label_list.append('m')
  return labeled_words_list, label_list

##  Merging the characters in s_ori into word sequence spe according to their segmentation labels;
def label2seg(chars, labels):
  if len(chars) > len(labels):
    return ' '.join(chars)
  new_line = ""
  word = ""
  FREE, COLLECT = range(2)
  state = FREE
  for i in range(len(chars)):
    if labels[i] == 'b' and state == FREE:
      word += chars[i]
      state = COLLECT
    elif labels[i] == 'm' and state == COLLECT:
      word += chars[i]
    elif labels[i] == 'e' and state == COLLECT:
      word += chars[i]
      new_line += word + ' '
      word = ""
      state = FREE
    elif labels[i] == 's' and state == FREE:
      new_line += chars[i] + ' '
  return new_line


## Labeling characters in s_ori with position labels;
def label_position(sequence):
  words_list = sequence.split()
  labeled_list = []
  for i in range(len(words_list)):
    labeled_list.append((words_list[i], i))
  return labeled_list

## Taking s_ori as a reference, filling the missing characters in s_sub and labeling them with label X;
def fill_sequence(refsequence, sequence):
  count = 0
  for i in range(len(refsequence)):
    # print "count, i",count, i, len(sequence), len(refsequence)
    if count >= len(sequence):
      sequence.append((refsequence[count][0], ('x', refsequence[i][1])))
      count += 1
    elif sequence[count][1][1] == refsequence[i][1]:
      # print "", refsequence[i]
      count += 1
      continue
    else:
      sequence.insert(count, (refsequence[count][0], ('x', refsequence[i][1])))
      count += 1
      # print "sequence", sequence
  return sequence

## Replacing label X with labels in L according to manually prepared rules;
def sentence_alignment(ori, sequence):
  ori_seq = label_position(ori)
  lab_seq, _, = label_BMES(sequence)


  lcs = LCS(lab_seq , ori_seq)
  # print "lcs", lcs
  fill =  fill_sequence(ori_seq, lcs)
  # print "fill", fill

  FREE, COLLECT, X = range(3)
  state = FREE
  res = ""
  word = ""
  for ch in fill:
    # print ch[1][0], state
    if (ch[1][0] == 's' or ch[1][0] == "e") and state == FREE:
      res += ch[0] + ' '
      word = ""
      state = FREE
    elif (ch[1][0] == "b" or ch[1][0] == 'm') and state == FREE:
      word = ch[0]
      state = COLLECT
    elif ch[1][0] == "e":
      word += ch[0]
      res += word + ' '
      word = ""
      state = FREE
    elif (ch[1][0] == "b") and (state == COLLECT or state == X):
      res += word + ' '
      word = ch[0]
      state = COLLECT
    elif (ch[1][0] == "m") and state == COLLECT:
      word += ch[0]
      state = COLLECT
    elif (ch[1][0] == "x") and state == FREE:
      # print "X!!!!!"
      word = ch[0]
      state = X
    elif (ch[1][0] == 's') and state == X:
      res += word + ' '
      res += ch[0] + ' '
      word = ""
      state = FREE
    elif (ch[1][0] == 'b') and state == X:
      res += word + ' '
      word = ch[0]
      state = COLLECT
    elif (ch[1][0] == 'x') and state == X:
      res += word + ' '
      word = ch[0]
      state = X
    elif (ch[1][0] == 'm') and state == X:
      state = COLLECT
      word += ch[0]
    elif (ch[1][0] == 'x') and state == COLLECT:
      word += ch[0]
      state = X
  if state != FREE:
    res += word
  return res

## counting characters number
def getLength(sequence):
  sequence = sequence.replace("UNK", "€")
  return len(' '.join(sequence.strip().decode('utf8')).encode('utf8').split())


def CWS_post_editing(orifilename, segfilename, outfilename):
  ori_sentences = open(orifilename, 'r').readlines()
  seg_sentences = open(segfilename, 'r').readlines()
  count = 0
  with open(outfilename, 'w') as outfile:
    for i in range(len(ori_sentences)):
      ori_sentence = ' '.join(ori_sentences[i].strip().decode('utf8')).encode('utf8')
      res = seg_sentences[i].strip()
      ori_length = getLength(ori_sentences[i])
      seg_length = getLength(seg_sentences[i])
      if ori_length != seg_length:
        print i
        res = ""      
        res = sentence_alignment(ori_sentence.strip(), seg_sentences[i].strip())
        print "ori", ori_sentences[i].strip()
        print "seg", seg_sentences[i].strip()
        print "res", res
        count += 1
      elif ori_length == seg_length and seg_sentences[i].find('UNK') >= 0:
        print i
        _, label_list = label_BMES(seg_sentences[i].strip())
        res = ""
        res = label2seg(ori_sentence.strip().split(), label_list)
        print "ori", ori_sentences[i].strip()
        print "seg", seg_sentences[i].strip()
        print "res", res
        count += 1

      outfile.write(res + '\n')

  print("Have edited %d sentence(s)." % count)


def main(argv):
  orifilename = "test_data/original_input.txt"
  segfilename = "test_data/segmented.txt"
  outfilename = "test_data/out.txt"
  try:
    """
    inputs:
    (1) original input file;
    (2) segmented inputfile (which is the output of the CWS system).
    output:
    (1) post-editing output file.
    """
    opts, args = getopt.getopt(argv,"h",["ori=","seg=", "out="])
  except getopt.GetoptError:
    print "Wrong Command Line Parameters!!!"
    print "Please refer to the format of the following command:"
    print '       python cws_postediting.py --ori=<original inputfile> --seg=<segmented inputfile> --out=<post-editing outputfile>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'cws_postediting.py --ori=<original inputfile> --seg=<segmented inputfile> --out=<post-editing outputfile>'
      sys.exit()
    elif opt == "--ori":
      orifilename = arg
      print orifilename
    elif opt == "--seg":
      segfilename = arg
      print segfilename
    elif opt == "--out":
      outfilename = arg
      print outfilename
  CWS_post_editing(orifilename, segfilename, outfilename)



if __name__ == "__main__":
  main(sys.argv[1:])

