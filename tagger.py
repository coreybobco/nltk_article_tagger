#!/usr/bin/env python
import collections
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

  def tag(self, article):
    pos_tokens = self.tokenize_part_of_speech(article)
    full_names = self.extract_names(pos_tokens)
    pos_tokens = self.group_proper_nouns(pos_tokens)
    # filtered_pos_tokens, multiword_proper_nouns = self.group_proper_nouns(pos_tokens)
    filtered_pos_tokens = self.filter_and_clean(pos_tokens)
    words_sorted_by_freq = self.sort_dict_by_frequency(self.get_word_frequencies(filtered_pos_tokens, full_names))
    name_tags = self.get_name_tags(words_sorted_by_freq, full_names)
    # place_tags = self.get_place_tags(words_sorted_by_freq)
    # topic_tags = self.get_topic_tags(words_sorted_by_freq)

  def extract_names(self, pos_tokens):
    '''NLTK's name recognition will try to classify proper noun phrases as persons, organizations, places, or 'other' (GPE). However, it doesn't work that well except for persons, and I've added some additional rules to handle common misclassifications.'''
    name_recognition_tokens = nltk.ne_chunk(pos_tokens)
    name_filter = self.config['name_filter'] 
    full_names = list()
    for token in name_recognition_tokens:
      if not isinstance(token, tuple) and token.label() == "PERSON":
          noun_phrase_as_list = list(token[0] for token in token.leaves())
          noun_phrase_list_copy = noun_phrase_as_list[:]
          for word in noun_phrase_list_copy:
            if word in name_filter:
              noun_phrase_as_list.remove(word)
          if len(noun_phrase_as_list) > 0 and noun_phrase_as_list[-1] != "County":
            last_word = noun_phrase_as_list[-1]
            if len(last_word) > 2 and last_word[-2:] == "'s":
              # Strip the 's from this name'
              noun_phrase_as_list[-1] = last_word[:-2]
            noun_phrase = " ".join(noun_phrase_as_list)
            if not noun_phrase in full_names:
              skip_adding_name = False
              for index, name in enumerate(full_names):
                if name in noun_phrase:
                  # Use the longer 'full' name instead
                  full_names[index] = name
                  skip_adding_name = True
                elif noun_phrase in name:
                  skip_adding_name = True
              if not skip_adding_name:
                full_names.append(noun_phrase)
    return full_names

  def filter_and_clean(self, pos_tokens):
    #Filter out tokens (words, punctuation) by part of speech or by checking against list of tokens
    #Clean extraneous punctuation from tokens
    filtered_pos_tokens = list()
    punct_tokens = self.config['punct_tokens']
    for token in pos_tokens:
      print(token[0].strip("".join(punct_tokens)))
      clean_token = (token[0].strip("".join(punct_tokens)), token[1])
      if self.filter_pos(token[1]) and self.filter_token(token[0]):
        filtered_pos_tokens.append(clean_token)
    return filtered_pos_tokens

  def filter_token(self, token):
    '''Filter out tokens that are punctuation, linking verbs, have verbs, etc. that cannnot be filtered using NLTK's POS tagger. In theory the part-of-speech filter should eliminate all verbs, but things like quotation marks for (embedded) quotes can make it misclassify parts of speech'''
    punct_tokens = self.config['punct_tokens']
    articles = self.config["articles"]
    linking_verbs = self.config["linking_verbs"]
    aux_verbs = self.config["aux_verbs"]
    abbreviations = self.config["abbreviations"]
    if token in punct_tokens or token.lower() in linking_verbs or token.lower() in aux_verbs or token.lower() in articles or token in abbreviations:
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

  def get_word_frequencies(self, pos_tokens, full_names):
    inflector = inflect.engine()
    frequency_dict = {}
    proper_noun_pos_list = ["NNP", "NNPS"]
    for token in pos_tokens:
      added_to_dict = False
      current_word = token[0]
      current_word_pos = token[1]
      if current_word_pos in proper_noun_pos_list:
        # See if the proper noun is part of a name, if so, just up the count for the full name to the dict
        for name in full_names:
          if current_word in name or name in current_word:
            if not name in frequency_dict.keys():
              frequency_dict[name] = 1
              added_to_dict = True
            else:
              frequency_dict[name] += 1
              added_to_dict = True
      if not added_to_dict:
        #Normalize words by singularizing plural nouns and lowercase mixed case words before adding to frequency dict
        if current_word_pos == "NNS":
          current_word = inflector.singular_noun(current_word)
        if not current_word.isupper() and not current_word.islower():
          current_word = current_word[0].lower() + current_word[1:]
        if current_word in frequency_dict:
          frequency_dict[current_word] += 1
        else: 
          frequency_dict[current_word] = 1
    # print(frequency_dict)
    return(frequency_dict)

  def sort_dict_by_frequency(self, frequency_dict):
    words_sorted_by_freq = {}
    for word, frequency in frequency_dict.items():
      if frequency in words_sorted_by_freq.keys():
          words_sorted_by_freq[frequency].append(word)
      else:
          words_sorted_by_freq[frequency] = [word]
    words_sorted_by_freq = collections.OrderedDict(sorted(words_sorted_by_freq.items(), reverse=True))
    print("---------")
    for frequency, wordlist in words_sorted_by_freq.items():
      print(str(frequency) + " --> " +", ".join(wordlist))
    print("---------")
    return words_sorted_by_freq


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
          if len(combo_token[0].split(" ")) > 1:
            processed_pos_tokens.append(combo_token)
          combo_token = ("","")
    return processed_pos_tokens #, multiword_proper_nouns

  def tokenize_part_of_speech(self, article):
    # TODO fix Trump's so same as Trump
    # article = article.replace("Trump's", "Drumpf")
    words = nltk.word_tokenize(article)
    pos_tokens = nltk.pos_tag(words)
    return pos_tokens





