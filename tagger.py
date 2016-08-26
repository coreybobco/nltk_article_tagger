#!/usr/bin/env python
import inflect
import re
import nltk

class Tagger_Class:
  def __init__(self):
    return

  def classify_pos(self, article):
    words = nltk.word_tokenize(article)
    pos_tokens = nltk.pos_tag(words)
    return pos_tokens

  def group_proper_nouns(self, pos_tokens):
    #Group nouns that occur right after each other as one word unit, i.e. "Associated Press", "news agency" and
    #rebuild data structure while also providing separate list
    proper_noun_filter = ["NNP", "NNPS"]
    processed_pos_tokens = list()
    multiword_proper_nouns = list()
    combo_token = ("","")
    for index, current_token in enumerate(pos_tokens):
      if index > 0:
        last_token = pos_tokens[index - 1]
        last_pos = last_token[1]
        current_pos = current_token[1]
        if last_pos not in proper_noun_filter:
          processed_pos_tokens.append(last_token)
          if current_pos in proper_noun_filter:
            combo_token = last_token
        elif last_pos in proper_noun_filter and current_pos in proper_noun_filter:
          combo_token = last_token
          combo_token = (last_token[0] + " " + current_token[0], current_token[1])
        elif last_pos in proper_noun_filter and current_pos not in proper_noun_filter: 
          # if combo_token == ("",""):
          #   print(last_token)
          #   print(current_token)
          processed_pos_tokens.append(combo_token)
          if len(combo_token[0].split(" ")) > 1:
            multiword_proper_nouns.append(combo_token[0])
    return processed_pos_tokens, multiword_proper_nouns

  def filter(self, pos_tokens):
    #Filter out tokens (words, punctuation) by part of speech or by checking against list of tokens    
    filtered_pos = list()
    for pos_token in pos_tokens:
      if self.filter_pos(pos_token[1]) and self.filter_token(pos_token[0]):
        print(pos_token)
        filtered_pos.append(pos_token)

  def filter_token(self, token):
    #Filter out tokens that are punctuation, linking verbs, have verbs, etc. that cannnot be filtered using NLTK's POS tagger
    punct_tokens = ["“", "”", "‘", "’", "—", ":", "(", ")", ]
    if token[0] in punct_tokens:
      if len(token) == 1:
        return False
      else:
        token = token[1:]
    if token[-1] in punct_tokens:
      if len(token) == 1:
        return False
      else:
        token = token[:-1]
    articles = ["a", "an", "the", "these", "those"]
    linking_verbs = ["be", "is", "are", "am", "was", "were", "been", "being", "'re", "appear", "become", "feel", "grow", "look", "remain", "seem", "smell", "sound", "stay", "taste"]
    aux_verbs = ["have", "had", "having", "has", "does", "do", "did"]
    abbreviations = ["Lt.", "Gov."]
    if token.lower() in punct_tokens or token in linking_verbs or token in aux_verbs or token in articles:
      return False
    else:
      return True

  def filter_pos(self, pos):
    '''POS filter will eliminate conjunctions, punctuation, prepositions, pronouns, determiners, modal auxiliary,
       comparative/superlative adjectives, ordinal adjectives, genitive marker ('s), item markers, existential there, foreign word, adverbs(?), verbs.
       For complete list open python3 console and nltk.help.upenn_tagset()'''
    pos_filter = ["''", ',', '.', 'CC', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RP', 'TO', 'WDT', 'WP', 'WP$', 'WRB', '``']
    if pos in pos_filter:
      return False
    else:
      return True

  def tag(self, article):
    pos_tokens = self.classify_pos(article)
    filtered_pos_tokens, multiword_proper_nouns = self.group_proper_nouns(pos_tokens)
    print(multiword_proper_nouns)
    #filtered_pos_tokens = self.filter(filtered_pos_tokens)

  def get_word_frequencies(self, pos_tokens, multiword_proper_nouns):
    inflector = inflect.engine()
    frequency_dictionary = {}
    plural_noun_filter = ["NNS", "NNPS"]
    for token in pos_tokens:
      current_word = token[0]
      if current_token[1] in plural_noun_filter:
        current_word = inflector.singular_noun(current_word)
        if len(token[0].split(" ")) > 1 and (token[1] == "NNP" or token[1] == "NNPS"):
          # Check 
      if current_token[0] in frequency_dictionary:
        frequency_dictionary[current_token] += 1
      else: 
        frequency_dictionary




