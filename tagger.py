#!/usr/bin/env python
import nltk

class Tagger_Class:
  def __init__(self):
    return

  def classify_pos(self, article):
    words = nltk.word_tokenize(article)
    pos_tokens = nltk.pos_tag(words)
    return pos_tokens

  def filter_pos(self, pos_tokens):
    #Filter out parts of speech that do not contribute to the tagging algorithm such as conjunctions, punctuation, etc
    #Token filter eliminates common words that the POS filter does not eliminate.
    token_filter = ["—", "be", "is", "are", "am", "was", "were", "been", "being"]
    '''POS filter will eliminate conjunctions, punctuation, prepositions, pronouns, determiners,
       comparative adjectives, adverbs(?)'''
    pos_filter = ["CC", ".", ",", "TO", "IN", "WDT", "PRP", "DT, "JJR", "RB"]
    filtered_pos = list()
    for pos_token in pos_tokens:
      if not pos_token[0] in token_filter and not pos_token[1] in pos_filter:
        print(pos_token)
        filtered_pos.append(pos_token)

  def tag(self, article):
    pos_tokens = self.classify_pos(article)
    self.filter_pos(pos_tokens)


