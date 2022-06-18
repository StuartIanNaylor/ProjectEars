SELECT words.word, count(files.file) as 'count'
 FROM words INNER JOIN files on words.word_id = files.word_id
  WHERE words.word='hey';
