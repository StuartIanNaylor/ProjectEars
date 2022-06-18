SELECT words.word, phones.phone1, phones.phone2, phones.phone3, phones.phone4, phones.phone5, phones.phone6, phones.phone7, phones.phone8, phones.phone9, phones.phone10, phones.phone11, phones.phone12, phones.phone13
 FROM words INNER JOIN phones on words.word_id = phones.word_id
  WHERE words.word='sheila';
