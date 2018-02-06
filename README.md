# tugbot
Python script to import formated data in Wikimedia Commons categories into Wikidata

This is only intended for semi-automated upload to Wikidata, you should check the result 
first without uploading, then if everything parses all right you can upload (--commit option) 
before double-checking the result and tidying if necessary

INSTALLATION
1. Install Pywikibot
2. Copy tugbot.py into pywiki/core/
3. Enjoy!

USAGE: tugbot.py [-h] [--commit] cat_name

Reads a Category from Commons described with the "Category definition: Object"
template, creates a Wikidata item and attempts to fill information from the
template into Wikidata

positional arguments:
  cat_name    name of the category to process

optional arguments:
  -h, --help  show this help message and exit
  --commit    sends results to Wikidata. Default is not to send.
  
example:
  ./tugbot.py Category:my_category     test run to see if everything parses correctly
  
  ./tugbot.py my_category              works as above

  ./tugbot.py "that's a cool cat"      escape category names containing special characters with quote marks
  
  ./tugbot.py my_category --commit     sends data to Wikidata
