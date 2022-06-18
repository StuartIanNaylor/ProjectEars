SELECT "words"."word", count("files"."file") as "count"
 FROM "words", "phones", "files" WHERE "words"."word_id" = "phones"."word_id" AND "words"."word_id" = "files"."word_id" AND
  "phones"."phone1" = 'SH' GROUP BY "words"."word"
