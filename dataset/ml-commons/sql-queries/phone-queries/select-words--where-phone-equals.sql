SELECT words.word
 FROM words INNER JOIN phones on words.word_id = phones.word_id
  WHERE phones.phone1='he';
