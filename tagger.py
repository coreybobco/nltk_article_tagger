#!/usr/bin/env python
import inflect
import json
import os
import re
import types
import nltk

class Tagger_Class:
  def __init__(self):
    self.config = json.load(open("config.json"))
    return

  def tokenize_part_of_speech(self, article):
    words = nltk.word_tokenize(article)
    pos_tokens = nltk.pos_tag(words)
    return pos_tokens

  def extract_names(self, pos_tokens):
    #NLTK's name recognition will try to classify proper noun phrases as persons, organizations, places, or 'other' (GPE)
    #However, it doesn't work that well except for persons, and I've added some additional rules to handle common misclassifications.
    name_recognition_tokens = nltk.ne_chunk(pos_tokens)
    name_filter = self.config['name_filter'] 
    full_names = list()
    for token in name_recognition_tokens:
      if not isinstance(token, tuple) and token.label() == "PERSON":
          noun_phrase_as_list = list(token[0] for token in token.leaves())
          noun_phrase_list_copy = noun_phrase_as_list[:]
          # noun_phrase_as_list = list()
          # for word_tuple in token.leaves():
          #   noun_phrase_as_list.append(word_tuple[0])
          for word in noun_phrase_list_copy:
            if noun_phrase_as_list[0] == "Texas":
              print(noun_phrase_as_list)
              print(word in name_filter)
            if word in name_filter:
              noun_phrase_as_list.remove(word)
          if len(noun_phrase_as_list) > 0 and noun_phrase_as_list[-1] != "County":
            noun_phrase = " ".join(noun_phrase_as_list)
            full_names.append(noun_phrase)
    print(full_names)
    return full_names


  def get_word_frequencies(self, pos_tokens, full_names):
    inflector = inflect.engine()
    frequency_dict = {}
    proper_noun_pos_list = ["NNP", "NNPS"]
    for token in pos_tokens:
      added_to_dict = false
      current_word = token[0]
      current_word_pos = token[1]
      if current_word_pos in proper_noun_pos_list:
        # See if the proper noun is part of a name, if so, just up the count for the full name to the dict
        for name in full_names:
          if current_word in name or name in current_word:
            if not name in frequency_dict.keys():
              frequency_dict[current_word] = 1
              added_to_dict = true
            else:
              frequency_dict[current_word] += 1
              added_to_dict = true
      if not added_to_dict:
        if current_word_pos == "NNS":
          current_word = inflector.singular_noun(current_word)
        if current_token[0] in frequency_dict:
          frequency_dict[current_token] += 1
        else: 
          frequency_dict[current_token] = 1
    # print(frequency_dict)

  def group_proper_nouns(self, pos_tokens):
    '''Group nouns that occur right after each other as one word unit, i.e. "Associated Press", "news agency" and rebuild data structure 
    while also providing separate list'''
    proper_noun_filter = ["NNP", "NNPS"]
    processed_pos_tokens = list()
    # multiword_proper_nouns = list()
    combo_token = ("","")
    for index, current_token in enumerate(pos_tokens):
      if index > 0:
        last_token = pos_tokens[index - 1]
        last_token_pos = last_token[1]
        current_token_pos = current_token[1]
        if last_token_pos not in proper_noun_filter:
          processed_pos_tokens.append(last_token)
        elif last_token_pos in proper_noun_filter and current_token_pos in proper_noun_filter:
          if combo_token == ("",""):
            combo_token = (last_token[0] + " " + current_token[0], current_token[1])
          else:
            combo_token = (combo_token[0] + " " + current_token[0], current_token[1])
        elif last_token_pos in proper_noun_filter and current_token_pos not in proper_noun_filter:
          if combo_token == ("", ""): 
            processed_pos_tokens.append(last_token)
          # if len(combo_token[0].split(" ")) > 1:
          #   multiword_proper_nouns.append(combo_token)
          combo_token = ("","")
    return processed_pos_tokens #, multiword_proper_nouns

  def filter(self, pos_tokens):
    #Filter out tokens (words, punctuation) by part of speech or by checking against list of tokens    
    filtered_pos = list()
    for token in pos_tokens:
      if self.filter_pos(token[1]) and self.filter_token(token[0]):
        # print(pos_token)
        filtered_pos.append(token)

  def filter_token(self, token):
    #Filter out tokens that are punctuation, linking verbs, have verbs, etc. that cannnot be filtered using NLTK's POS tagger
    punct_tokens = self.config['punct_tokens']
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
    articles = self.config["articles"]
    linking_verbs = self.config["linking_verbs"]
    aux_verbs = self.config["aux_verbs"]
    abbreviations = self.config["abbreviations"]
    if token.lower() in punct_tokens or token in linking_verbs or token in aux_verbs or token in articles:
      return False
    else:
      return True

  def filter_pos(self, pos):
    '''POS filter will eliminate conjunctions, punctuation, prepositions, pronouns, 
    determiners, modal auxiliary, comparative/superlative adjectives, ordinal adjectives, 
    genitive marker ('s), item markers, existential there, foreign word, adverbs(?), verbs.
    For complete list open python3 console and nltk.help.upenn_tagset()'''
    pos_filter = self.config["pos_filter_parts"]
    if pos in pos_filter:
      return False
    else:
      return True

  def tag(self, article):
    pos_tokens = self.tokenize_part_of_speech(article)
    full_names = self.extract_names(pos_tokens)
    pos_tokens = self.group_proper_nouns(pos_tokens)
    # filtered_pos_tokens, multiword_proper_nouns = self.group_proper_nouns(pos_tokens)
    filtered_pos_tokens = self.filter(pos_tokens)
    self.get_word_frequencies(filtered_pos_tokens, full_names)






