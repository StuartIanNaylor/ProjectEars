SELECT words.word, syllables.syllable1, syllables.syllable2, syllables.syllable3, syllables.syllable4, syllables.syllable5, syllables.syllable6, syllables.syllable7, syllables.syllable8, syllables.syllable9
 FROM words INNER JOIN syllables on words.word_id = syllables.word_id
  WHERE words.word='sheila';
