#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Natural Language Toolkit: Tokenizers
#
# Copyright (C) 2001-2022 NLTK Project
# Author: Christopher Hench <chris.l.hench@gmail.com>
#         Alex Estes
# URL: <https://www.nltk.org>
# For license information, see LICENSE.TXT

"""
The Sonority Sequencing Principle (SSP) is a language agnostic algorithm proposed
by Otto Jesperson in 1904. The sonorous quality of a phoneme is judged by the
openness of the lips. Syllable breaks occur before troughs in sonority. For more
on the SSP see Selkirk (1984).

The default implementation uses the English alphabet, but the `sonority_hiearchy`
can be modified to IPA or any other alphabet for the use-case. The SSP is a
universal syllabification algorithm, but that does not mean it performs equally
across languages. Bartlett et al. (2009) is a good benchmark for English accuracy
if utilizing IPA (pg. 311).

Importantly, if a custom hierarchy is supplied and vowels span across more than
one level, they should be given separately to the `vowels` class attribute.

References:

- Otto Jespersen. 1904. Lehrbuch der Phonetik.
  Leipzig, Teubner. Chapter 13, Silbe, pp. 185-203.
- Elisabeth Selkirk. 1984. On the major class features and syllable theory.
  In Aronoff & Oehrle (eds.) Language Sound Structure: Studies in Phonology.
  Cambridge, MIT Press. pp. 107-136.
- Susan Bartlett, et al. 2009. On the Syllabification of Phonemes.
  In HLT-NAACL. pp. 308-316.
"""
import argparse
import os
import sqlite3
import glob
import nltk
nltk.download('punkt')

import re
import warnings
from string import punctuation

from nltk.tokenize.api import TokenizerI
from nltk.util import ngrams
from nltk.tokenize import SyllableTokenizer
from nltk import word_tokenize

from nltk.corpus import cmudict
nltk.download('cmudict')

def createDB(source_dir='en/clips', database='ml-commons.db'):

  if not os.path.exists(source_dir):
    print("Source_dir " + source_dir + " does not exist")
    exit()

  con = sqlite3.connect(database)
  cur = con.cursor()
  SQL = "DROP TABLE words;"
  try:
    cur.execute(SQL)
  except sqlite3.OperationalError:
    print("no such table: words")
  
  SQL="CREATE TABLE words (word_id INTEGER PRIMARY KEY, word TEXT NOT NULL);"
  cur.execute(SQL)
  
  SQL = "DROP TABLE syllables;"
  try:
    cur.execute(SQL)
  except sqlite3.OperationalError:
    print("no such table: phones_sylables")
  
  SQL="CREATE TABLE syllables (word_id INTEGER, "
  syllable_count = 1
  SQL_syllables = ""
  while syllable_count < 10:
    SQL_syllables = SQL_syllables + "syllable" + str(syllable_count) + " TEXT, "
    syllable_count += 1
  SQL_syllables = SQL_syllables + "sylable INTEGER);"
  SQL = SQL + SQL_syllables
  #print(SQL)
  cur.execute(SQL)

  SQL = "DROP TABLE phones;"
  try:
    cur.execute(SQL)
  except sqlite3.OperationalError:
    print("no such table: phones")
  
  SQL="CREATE TABLE phones (word_id INTEGER, "
  phone_count = 1
  SQL_phones = ""
  while phone_count < 20:
    SQL_phones = SQL_phones + "phone" + str(phone_count) + " TEXT, "
    phone_count += 1
  SQL_phones = SQL_phones + "phone INTEGER);"
  SQL = SQL + SQL_phones
  #print(SQL)
  cur.execute(SQL)
    
  SQL = "DROP TABLE files;"
  try:
    cur.execute(SQL)
  except sqlite3.OperationalError:
    print("no such table: files")
  
  SQL="CREATE TABLE files (word_id INTEGER, file TEXT NOT NULL);"
  #print(SQL)
  cur.execute(SQL)
  
  con.commit()
  dir_contents = os.listdir(source_dir)
  SSP = SyllableTokenizer()
  phone_dict = cmudict.dict()
  
  for word_s in dir_contents:
    if os.path.isdir(source_dir + "/" + word_s):
      #cmudict is used as other language dictionaries can be used but is slow and dictionary is limited
      #Lang models can be found *.dic https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/
      #https://github.com/cmusphinx/g2p-seq2seq is good but lacks sylables (from what I can see) so is not used as a fallback
      #also cmudict is not all that accurate but it doesn't matter but purely we can the same results for what we are analysing
      #as we are looking for simularities not phonetic / sylable accuracy

      syllables  = SSP.tokenize(word_s)
      syllables_count = len(syllables)
      pronounces = phone_dict.get(word_s)
      if pronounces == None:
        phones = None
      else:
        phones = pronounces[0]
        phones_count = len(phones)
          
      if syllables == None or phones == None:
        print(word_s + " is not in the dictionary")
      else:
        print(f"WORD({word_s!r}) yields {syllables} SYLABLE COUNT is {syllables_count} ")
        SQL = "INSERT INTO words (word) VALUES ('" + word_s + "')"
        cur.execute(SQL)
        word_lastrowid = cur.lastrowid
        #print(word_lastrowid)
        SQL = "INSERT INTO syllables (word_id, "
        syllable_count = 1
        SQL_fields = ""
        SQL_values = ""
        for syllable in syllables:
          if syllable_count < syllables_count:
            SQL_fields = SQL_fields + "syllable" + str(syllable_count) + ", "
            SQL_values = SQL_values + str(syllable)  + "', '"
          else:
            SQL_fields = SQL_fields + "syllable" + str(syllable_count) + ", sylable) VALUES ("
            SQL_values = SQL_values + str(syllable)  + "'," + str(syllables_count) + ")"
          syllable_count += 1
        SQL = SQL + SQL_fields + str(word_lastrowid) + ", '" + SQL_values
        #print(SQL)
        cur.execute(SQL)

        print(f"WORD({word_s!r}) yields {phones} PHONE COUNT is {phones_count} ")
        SQL = "INSERT INTO phones (word_id, "
        phone_count = 1
        SQL_fields = ""
        SQL_values = ""
        for phone in phones:
          if phone_count < phones_count:
            SQL_fields = SQL_fields + "phone" + str(phone_count) + ", "
            SQL_values = SQL_values + str(phone)  + "', '"
          else:
            SQL_fields = SQL_fields + "phone" + str(phone_count) + ", phone) VALUES ("
            SQL_values = SQL_values + str(phone)  + "'," + str(phones_count) + ")"
          phone_count += 1
        SQL = SQL + SQL_fields + str(word_lastrowid) + ", '" + SQL_values
        #print(SQL)
        cur.execute(SQL)
        
        for filename in glob.glob(os.path.join(source_dir + "/" + word_s, '*.opus')):
          #print(os.path.basename(filename))
          SQL = "INSERT INTO files (word_id, file) values(" + str(word_lastrowid) + ",'" + os.path.basename(filename) + "');"
          cur.execute(SQL)
      con.commit()
  

class SyllableTokenizer(TokenizerI):
    """
    Syllabifies words based on the Sonority Sequencing Principle (SSP).

        >>> from nltk.tokenize import SyllableTokenizer
        >>> from nltk import word_tokenize
        >>> SSP = SyllableTokenizer()
        >>> SSP.tokenize('justification')
        ['jus', 'ti', 'fi', 'ca', 'tion']
        >>> text = "This is a foobar-like sentence."
        >>> [SSP.tokenize(token) for token in word_tokenize(text)]
        [['This'], ['is'], ['a'], ['foo', 'bar', '-', 'li', 'ke'], ['sen', 'ten', 'ce'], ['.']]
    """

    def __init__(self, lang="en", sonority_hierarchy=False):
        """
        :param lang: Language parameter, default is English, 'en'
        :type lang: str
        :param sonority_hierarchy: Sonority hierarchy according to the
                                   Sonority Sequencing Principle.
        :type sonority_hierarchy: list(str)
        """
        # Sonority hierarchy should be provided in descending order.
        # If vowels are spread across multiple levels, they should be
        # passed assigned self.vowels var together, otherwise should be
        # placed in first index of hierarchy.
        if not sonority_hierarchy and lang == "en":
            sonority_hierarchy = [
                "aeiouy",  # vowels.
                "lmnrw",  # nasals.
                "zvsf",  # fricatives.
                "bcdgtkpqxhj",  # stops.
            ]

        self.vowels = sonority_hierarchy[0]
        self.phoneme_map = {}
        for i, level in enumerate(sonority_hierarchy):
            for c in level:
                sonority_level = len(sonority_hierarchy) - i
                self.phoneme_map[c] = sonority_level
                self.phoneme_map[c.upper()] = sonority_level


    def assign_values(self, token):
        """
        Assigns each phoneme its value from the sonority hierarchy.
        Note: Sentence/text has to be tokenized first.

        :param token: Single word or token
        :type token: str
        :return: List of tuples, first element is character/phoneme and
                 second is the soronity value.
        :rtype: list(tuple(str, int))
        """
        syllables_values = []
        for c in token:
            try:
                syllables_values.append((c, self.phoneme_map[c]))
            except KeyError:
                if c not in punctuation:
                    warnings.warn(
                        "Character not defined in sonority_hierarchy,"
                        " assigning as vowel: '{}'".format(c)
                    )
                    syllables_values.append((c, max(self.phoneme_map.values())))
                    self.vowels += c
                else:  # If it's a punctuation, assign -1.
                    syllables_values.append((c, -1))
        return syllables_values


    def validate_syllables(self, syllable_list):
        """
        Ensures each syllable has at least one vowel.
        If the following syllable doesn't have vowel, add it to the current one.

        :param syllable_list: Single word or token broken up into syllables.
        :type syllable_list: list(str)
        :return: Single word or token broken up into syllables
                 (with added syllables if necessary)
        :rtype: list(str)
        """
        valid_syllables = []
        front = ""
        for i, syllable in enumerate(syllable_list):
            if syllable in punctuation:
                valid_syllables.append(syllable)
                continue
            if not re.search("|".join(self.vowels), syllable):
                if len(valid_syllables) == 0:
                    front += syllable
                else:
                    valid_syllables = valid_syllables[:-1] + [
                        valid_syllables[-1] + syllable
                    ]
            else:
                if len(valid_syllables) == 0:
                    valid_syllables.append(front + syllable)
                else:
                    valid_syllables.append(syllable)

        return valid_syllables


    def tokenize(self, token):
        """
        Apply the SSP to return a list of syllables.
        Note: Sentence/text has to be tokenized first.

        :param token: Single word or token
        :type token: str
        :return syllable_list: Single word or token broken up into syllables.
        :rtype: list(str)
        """
        # assign values from hierarchy
        syllables_values = self.assign_values(token)

        # if only one vowel return word
        if sum(token.count(x) for x in self.vowels) <= 1:
            return [token]

        syllable_list = []
        syllable = syllables_values[0][0]  # start syllable with first phoneme
        for trigram in ngrams(syllables_values, n=3):
            phonemes, values = zip(*trigram)
            #print(phonemes, values)
            # Sonority of previous, focal and following phoneme
            prev_value, focal_value, next_value = values
            # Focal phoneme.
            focal_phoneme = phonemes[1]

            # These cases trigger syllable break.
            if focal_value == -1:  # If it's a punctuation, just break.
                syllable_list.append(syllable)
                syllable_list.append(focal_phoneme)
                syllable = ""
            elif prev_value >= focal_value == next_value:
                syllable += focal_phoneme
                syllable_list.append(syllable)
                syllable = ""

            elif prev_value > focal_value < next_value:
                syllable_list.append(syllable)
                syllable = ""
                syllable += focal_phoneme

            # no syllable break
            else:
                syllable += focal_phoneme

        syllable += syllables_values[-1][0]  # append last phoneme
        syllable_list.append(syllable)

        return self.validate_syllables(syllable_list)
        syllable_list.append(syllable)

        return self.validate_syllables(syllable_list)



def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', type=str, default='en/clips', help='dest dir location default=out')
  parser.add_argument('--database', type=str, default='ml-commons.db', help='database name default=ml-commons.db')
  args = parser.parse_args()

   
  
  createDB(args.source_dir,args.database)

    
if __name__ == '__main__':
  main_body()
  
  
  
