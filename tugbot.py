#!/usr/bin/python3
import pywikibot
import re

_langswitch_tokens = ["Langswitch", "LangSwitch", "langswitch"]
site_commons  = pywikibot.Site("commons", "commons")
site_wikidata = pywikibot.Site("wikidata", "wikidata")
#site_wikidata = pywikibot.Site("test", "wikidata")
repo_wikidata = site_wikidata.data_repository()

#--------------------
def get_image(work):
    work = work.split("image")[1]
    work = work.replace("=","").strip()
    work = work.split("|")[0]
    return work.strip()

def detect_langswitch(work):
    for i in _langswitch_tokens:
        if i in work: return True
    return False

def detect_langtags(work): # Detects tags of the form "{{de|Lampe}} {{en|lamp}} {{fr|lampe}}"
    matchObj = re.match( r'{{(..)\|(.*?)}}', work)
    if matchObj: return True
    return False
    
def split_langtags(work):
    language_fields = work.split("{{")
    lang_values_dict = {}
    for language_field in language_fields:
        #print ("language_field : ", language_field)
        matchObj = re.match( r'(..)\|(.*?)}}', language_field)
        if matchObj:
            lang_code = matchObj.group(1)
            value     = matchObj.group(2)
            #print ("     lang_code:", lang_code)
            #print ("     value    :", value)
            lang_values_dict [lang_code] = value
    return lang_values_dict

def split_langswitch(work):
    for i in _langswitch_tokens:
        if i in work: work = work.split(i)[1]
    work = work.split("}}")[0]
    
    lang_values = [i.strip() for i in work.split("\n")]
    lang_values = list(filter(None, lang_values))
    lang_values_dict = {}
    for lang_value in lang_values:
        lang_value_split = lang_value.split("=")
        lang  = lang_value_split[0]
        lang  = lang.strip()
        lang  = lang.replace("|","")
        value = "" # Need to be ready for empty strings
        if len(lang_value_split) > 1: value = lang_value_split[1]
        lang_values_dict[lang] = value.strip()
    return lang_values_dict

#def get_title(work):
    #work = work.split("title")[1]
    #if detect_langswitch(work):
        #return split_langswitch(work)
    ##elif: ### Will need to manage the {{en|blablabla}} type titles
    #else:
        #return {"en": work}

def split_institution(work):
    work = work.split("{{Institution:")[1]
    work = work.split("}}")[0]
    return work.strip()

def get_institution(work):
    #work = work.split("institution")[1]
    work = get_field(work, "institution")
    if detect_langswitch(work):
        return split_langswitch(work)['en']
    #elif: ### Will need to manage the {{en|blablabla}} type titles
    #elif ("{{Institution" in work):
    #    return split_institution(work)
    else:
        return work

def get_field(work, field):
    work = work.split(field, 1)[1]
    work = work.replace("=", "", 1)
    
    # Detects end of the field. Will need to improve this.
    # work = work.split("\n|")[0]
    text_to_keep = ""
    curly_bracket_counter = 0
    for i in work:
        if (i == "|") and (curly_bracket_counter == 0): 
            break
        elif (i == "{"): curly_bracket_counter += 1
        elif (i == "}"): curly_bracket_counter -= 1
        text_to_keep += i
        #print('    ', text_to_keep, curly_bracket_counter)
    work = text_to_keep
    # remove unneeded elements
    work = work.replace("<br>","")
    work = work.replace("<br/>","")
    work = work.replace("<br />","")    
    return work.strip()

def get_multilingual_text_field(work, field):
    work = get_field(work, field)
    if work.strip() == "": return None
    
    if detect_langswitch(work):
        return split_langswitch(work)
    elif detect_langtags(work):
        return split_langtags(work)
    else:
        return {"en": work}

#....................
_epoch_dict = {
                "day"        : 11,
                "year"       : 9,
                "century"    : 7,
                "millennium" : 6
              }

def get_epoch(work):
    if "century" in work:
        return "century"
    elif "millennium" in work:
        return "millennium"
    else:
        return "year"

def split_epoch(work):
    # date_number = [s for s in work.split() if s.isdigit()][0]
    
    date_number = ""
    matchObj = re.search( r'(\d+)', work)
    if matchObj: 
        date_number = matchObj.group(1)
    else:
        return None
    return date_number

def split_complex_date(work):
    epoch = ""
    if "century" in work:
        epoch = "century"
    elif "millennium" in work:
        epoch = "millennium"
    work = work.replace("}}","")
    #work = [s for s in work.split("|") if s.isdigit()][0]
    fields_list = [s for s in work.split("|")]
    fields_list = [s.replace("date=","") for s in fields_list]
    fields_list = [s.replace("date1=","") for s in fields_list]
    fields_list = [s.replace("date2=","") for s in fields_list]
    work = [s for s in fields_list if s.strip().isdigit()][0]
    work = work+ " " + epoch
    return split_epoch(work)

def split_date(work):
    work = work.replace("{{date","")
    work = work.replace("}}","")
    epoch = ""
    if "century" in work:
        epoch = "century"
    elif "millennium" in work:
        epoch = "millennium"
    work = [s for s in work.split("|") if s.isdigit()][0]
    work = work+ " " + epoch
    return split_epoch(work)

def date_is_circa(work):
    work = work.split("|date", 1)[1]
    work = work.split("\n|")[0]    
    if ("circa" in work) or ("?" in work):
        return True
    return False

def date_is_BCE(work):
    work = work.split("|date", 1)[1]
    work = work.split("\n|")[0]    
    if ("BC" in work) or ("BCE" in work):
        return True
    return False

def get_date(work):
    #work = work.split("|date", 1)[1]
    #work = work.split("\n|")[0]
    work = get_field(work, "date")
    if work.replace("=","").strip() == "": return None
    date_claim_target = ""
    if ('{{complex date' in work):
        date_claim_target = split_complex_date(work)
    elif ('{{other date' in work):
        date_claim_target = split_complex_date(work)
    elif ('{{otherdate' in work):
        date_claim_target = split_complex_date(work)
    elif ('{{date' in work):
        date_claim_target = split_date(work)
    #elif: #other date templates
    else:
        date_claim_target =  split_epoch(work)
    
    if date_is_BCE(page.text): 
        #date_claim_target = "-"+date_claim_target
        date_claim_target = -int(date_claim_target)-1
    return date_claim_target
#....................
def get_type(work):
    work = work.split("|type")[1]
    work = work.split("=")[1]
    work = work.split("\n|")[0]
    return work.strip().lower()
#....................
def dimension_dict_is_empty(dimension_dict):
    work = dimension_dict.copy()
    if 'unit' in work: del work['unit']
    for i in work:
        if work[i] != "": return False
    return True

def split_size(work):
    if work.strip() == "": return ""
    work = work.replace("{{Size","")
    work = work.replace("}}","")
    dimensions = work.split("|")
    dimension_dict = {}
    _length_units_list = ['m', 'cm', 'mm']
    _mass_units_list   = ['g', 'kg']
    for dimension in dimensions:
        if dimension.strip() == "": continue
        dimension_split = dimension.split("=")
        dimension_name  = dimension_split[0]
        dimension_value = ""
        # sometimes units are given by {{Size|cm|height=8.4|width=8.9|depth=1.4}}
        if dimension_name in _length_units_list: dimension_dict["unit"] = dimension_name.strip()
        if dimension_name in _mass_units_list  : dimension_dict["mass_unit"] = dimension_name.strip()
        
        if len(dimension_split) > 1: dimension_value = dimension_split[1]
        if not dimension_value.strip() == '':
            if dimension_name == "unit" and dimension_value.strip() in _length_units_list:
                dimension_dict["unit"] = dimension_value.strip()
            elif dimension_name == "unit" and dimension_value.strip() in _mass_units_list:
                dimension_dict["mass_unit"] = dimension_value.strip()
            else:
                dimension_dict[dimension_name] = dimension_value.strip()
    if not dimension_dict_is_empty(dimension_dict): return dimension_dict
    return None

def get_dimension(work):
    work = get_field(work, "dimensions")
    #print("====================")
    #print (work)
    #print("--------------------")
    if ("{{Size" in work): work = split_size(work)
    if work == {'unit': ''}: return None
    return work
#....................
def split_technique(work):
    if work.strip() == "": return ""
    work = work.replace("{{Technique","")
    work = work.replace("{{technique","")
    work = work.replace("}}","")
    techniques = work.split("|")
    techniques = [i for i in techniques if i !='']
    return techniques

def get_medium(work):
    work = get_field(work, "medium")
    work = work.replace("and=","").strip().lower()  
    work = work.replace("and1=","").strip().lower()  
    work = work.replace("and2=","").strip().lower()
    work = work.replace("and3=","").strip().lower()     
    work = work.replace("and4=","").strip().lower()  
    work = work.replace("and5=","").strip().lower()
    work = work.replace("and6=","").strip().lower() 
    
    medium_list = []
    if detect_langswitch(work):
        medium_list = split_langswitch(work)['en'].split(",")
    elif ("{{Technique" in work) or ("{{technique" in work):
        medium_list = split_technique(work)
    medium_list = [s.strip() for s in medium_list]    
    return medium_list
#....................
def get_references(work):
    work = get_field(work, "references")
    work = work.split("\n}}")[0]
    link_dict = {}
    if "[http" in work:
        link_list = work.split("\n")
        for link in link_list:
            link = link.replace("[","")
            link = link.replace("]","")
            link_url   = link.split(" ")[0]
            link_title = link.replace(link_url,"")
            link_dict[link_url] = link_title.strip()
    if len(link_dict) == 0: return None
    return link_dict

def get_Louvre_online(work):
    work = get_field(work, "references")
    if("{{Louvre online") in work:
        work = work.replace("}}", "")
        if work.split("|"): return work.split("|")[1].split()[0]
    return None
#.......................
def get_scale(work): # Detects scale"
    matchObj = re.search( r'1[/:](\d+)', work)
    if matchObj: return matchObj.group(1)
    return None
#.......................
def split_ProvenanceEvent(work, field):
    if not field in work: return None
    work = work.replace("}}","")
    work = work.split(field)
    if len(work) == 0: return None
    work = work[1].replace("=","").strip()
    work = work.split("|")[0].strip()
    return work

def get_provenance_date(work):
    work = get_field(work, "object history")
    if ("ProvenanceEvent") in work: work = split_ProvenanceEvent(work, "time")
    else: work = split_epoch(work)
    return work

def get_provenance_name(work):
    work = work.lower()
    
    synonym_list_gift     = ["gift", "gifted", "offer", "offered", "given"]
    synonym_list_purchase = ["purchase", "purchased", "purchasing", "bought"]
    synonym_list_lent     = ["lent", "lease", "leasing"]
    
    for word in work.split():
        if   (word in synonym_list_gift    ): return "Q184303"
        elif (word in synonym_list_purchase): return "Q1369832"
        elif (word in synonym_list_lent    ): return "Q716894"
    return None

    
def get_provenance_cause(work):
    work = get_field(work, "object history")
    if ("ProvenanceEvent") in work: work = split_ProvenanceEvent(work, "type")
    work = get_provenance_name(work)
    return work
    
def get_provenance_donator(work):
    work = get_field(work, "object history")
    if ("ProvenanceEvent") in work: work = split_ProvenanceEvent(work, "oldowner")
    else: work = None # free-form not yet implemented
    return work
#.......................
def get_inventory_number(work):
    work = get_field(work, "accession number")
    # manages stuff such as "{{Louvre number|AO 12454}}"
    if ("{{" in work) and ("}}" in work):
        work = work.replace("}}", "")
        if work.split("|"): work = work.split("|")[1]   # this is very crude but will do for now
    return work
#.......................


#--------------------

#=== WIKIDATA DATA AND FUNCTIONS ======================================

_P_image            = "P18"
_P_type             = "P31"
_P_artist           = "P170"
_P_title            = "P1476"
#_P_description = # not in Claims
_P_date             = "P571"
_P_institution      = "P195"
_P_start_time       = "P580"
_P_has_cause        = "P828"
_P_donated_by       = "P1028"

_P_heigth           = "P2048"
_P_length           = "P2043"
_P_width            = "P2049"
_P_thickness        = "P2610"
_P_diameter         = "P2386"
_P_mass             = "P2067"
_P_scale            = "P1752"

_P_medium           = "P186"
_P_inscriptions     = "P1684"
_P_location         = "P276"
_P_accession_number = "P217"
#_P_notes            = ""   # Does not seem to exist
_P_references       = "P973"
_P_commons_cat      = "P373"

_P_circa            = "P1480"
_Q_circa            = "Q5727902"

_P_Atlas_ID         = "P1212"

_type_Q_numbers = {
                    "painting" : "Q3305213"
                  }
                  

_medium_Q_numbers   = {
                        "wood"                : "Q287",
                        "plant fiber"         : "Q20026824",
                        "vegetable fiber"     : "Q20026824",
                        "vegetable fibre"     : "Q20026824",
                        "hair"                : "Q28472",
                        "copper"              : "Q753",
                        "silver"              : "Q1090",
                        "gold"                : "Q897",
                        "steel"               : "Q11427",
                        "metal"               : "Q11426",
                        "maple wood"          : "Q402516",
                        "cotton"              : "Q11457",
                        "iron"                : "Q677",
                        "marble"              : "Q40861",
                        "bronze"              : "Q34095",
                        "brass"               : "Q39782",
                        "terracotta"          : "Q60424", 
                        "terra cotta"         : "Q60424", 
                        "synthetic materials" : "Q3300022",
                        "synthetic material"  : "Q3300022",
                        "ivory"               : "Q82001", 
                        "ebony"               : "Q156005",
                        "bone"                : "Q814769",
                        "oil"                 : "Q296955",
                        "oil paint"           : "Q296955",
                        "canvas"              : "Q12321255"
                      } 

_unit_Q_numbers = {
                    "cm" : "Q174728", 
                    "m"  : "Q11573", 
                    "mm" : "Q174789",
                    "kg" : "Q11570",
                    "g"  : "Q41803"
                  } 

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict, summary="Setting labels")
    # Add description here or in another function
    return new_item.getID()

def get_Q_number(label):
    from pywikibot import pagegenerators, WikidataBot
    sparql = "SELECT ?item WHERE { ?item rdfs:label '"+label+"'@en }"
        
    entities = pagegenerators.WikidataSPARQLPageGenerator(sparql, site=repo_wikidata)
    entities = list(entities)
    
    #if len(entities) == 0:
        #sparql = "SELECT ?item WHERE { ?item rdfs:altLabel '"+label+"'@en }"
        #entities = pagegenerators.WikidataSPARQLPageGenerator(sparql, site=repo_wikidata)
        #entities = list(entities)
    return entities

def get_image_page(image_name):
    from pywikibot import FilePage
    page = pywikibot.FilePage(site_commons, image_name)
    return page

def get_type_Q_number(work):
    if work in _type_Q_numbers:
        # we put this in a one-item list for compatibility with what Wikidata returns.
        work = [ pywikibot.ItemPage(repo_wikidata, _type_Q_numbers[work]) ]
    else:
        work = get_Q_number(work)
    return work
 
def get_medium_Q_numbers(page_text):
    medium_list           = get_medium(page_text)
    medium_Q_numbers_list = []
    for i in medium_list:
        if i in _medium_Q_numbers: 
            # we put this in a one-item list for compatibility with what Wikidata returns.
            medium_Q_numbers_list.append( [ pywikibot.ItemPage(repo_wikidata, _medium_Q_numbers[i]) ] )
        else:
            #print("   ", i, get_Q_number(i))
            medium_Q_numbers_list.append(get_Q_number(i))
    return medium_Q_numbers_list

def get_unit_Q_numbers(work):
    if work in _unit_Q_numbers:
        return pywikibot.ItemPage(repo_wikidata, _unit_Q_numbers[work])
    else:
        return None
        #return get_Q_number(i)[0] 

def get_artist_Q_number(page_text):
    if ("{{Creator:" in page_text):
        creator_page = page_text.replace("{{", "")
        creator_page = creator_page.replace("}}", "")
        creator_text = pywikibot.Page(site_commons, creator_page).text
        matchObj = re.search( r'[wW]ikidata *= *(Q\d+)', creator_text)
        creator_Q_number = ""
        if matchObj: 
            creator_Q_number = matchObj.group(1)
            return pywikibot.ItemPage(repo_wikidata, creator_Q_number )
        
    anonymous_item = pywikibot.ItemPage(repo_wikidata, "Q4233718" )
    if ("anonymous" in page_text.lower()) or ("unknown" in page_text.lower()):
        return anonymous_item
    else:
        artist_list = get_Q_number(page_text)
        if len(artist_list) > 0:
            return artist_list[0]
        return None

def get_institution_q_item(page_text):
    if ("{{Institution:" in page_text):
        institution_page = page_text.replace("{{", "")
        institution_page = institution_page.replace("}}", "")
        institution_text = pywikibot.Page(site_commons, institution_page).text
        
        #print ("========================")
        #print (institution_text )
        #print ("========================")
        matchObj = re.search( r'[wW]ikidata *= *(Q\d+)', institution_text)
        institution_Q_number = ""
        if matchObj: 
            institution_Q_number = matchObj.group(1)
            return pywikibot.ItemPage(repo_wikidata, institution_Q_number )
    return None

#=========================================
import argparse
parser = argparse.ArgumentParser(description='Reads a Category from Commons described with the "Category definition: Object" template, creates a Wikidata item and attempts to fill information from the template into Wikidata')
parser.add_argument('cat_name', help='name of the category to process')
parser.add_argument('--commit', action="store_true", help='sends results to Wikidata. Default is not to send.')
args = parser.parse_args()


#commons_cat = "Scale model of Capricieux-MnM 7 MG 8"
commons_cat = args.cat_name
if not ( commons_cat.startswith("Category:") or commons_cat.startswith("category:") ):
    commons_cat = "Category:"+commons_cat

pollute_wikidata = args.commit

page = pywikibot.Page(site_commons, commons_cat)

if ("User:Rama/Catdef" in page.text):
    print("YOU FORGOT TO GIVE A NEW CATEGORY AS ARGUMENT AGAIN, IDIOT")
    exit()


print ("  Image            =", get_image(page.text))
#type_q_items = get_Q_number(get_type(page.text))
type_q_items = get_type_Q_number(get_type(page.text))
print ("  Type             =", get_type(page.text), type_q_items )
text_artist = None
text_artist_dict = get_multilingual_text_field(page.text, "artist")
if text_artist_dict: 
    text_artist = text_artist_dict['en']
    #text_artist = text_artist.replace("{{Creator:", "")
    #text_artist = text_artist.replace("}}", "")
    print ("  Artist           =", text_artist, get_artist_Q_number(text_artist) )
print ("  Title            =", get_multilingual_text_field(page.text, "title"))
descriptions = get_multilingual_text_field(page.text, "description")
if descriptions:
    for lang in descriptions:
        # truncate description to avoid failure when committing
        if len(descriptions[lang]) > 249: descriptions[lang] = descriptions[lang][:249] 
print ("  Description      =", descriptions )
print ("  Date             =", get_date(page.text), get_epoch(page.text) )
print ("  Dimensions       =", get_dimension(page.text))
print ("  Scale            =", get_scale(page.text))
print ("  Medium           =", get_medium(page.text))
#print ( get_medium_Q_numbers(page.text) )
text_inscriptions = get_multilingual_text_field(page.text, "inscriptions")
print ("  Inscriptions     =", text_inscriptions )
institution_q_item = get_institution_q_item(get_institution(page.text))
print ("  Institution      =", get_institution(page.text), institution_q_item  )
text_location = get_multilingual_text_field(page.text, "location")
if text_location:
    print ("  Location         =", text_location['en'], get_Q_number(text_location['en']))
text_object_history = get_field(page.text, "object history")
print ("  Object history   =", get_multilingual_text_field(page.text, "object history"))
if text_object_history:
    print ("  Object history   =", get_provenance_date(page.text), get_provenance_cause(page.text), get_provenance_donator(page.text) )
print ("  Accession number =", get_inventory_number(page.text) )
print ("  Notes            =", get_multilingual_text_field(page.text, "notes"))
text_reference = get_references(page.text)
print ("  References       =", text_reference)
if get_Louvre_online(page.text):
    print ("  Louvre online    =", get_Louvre_online(page.text) )
print ("  Commons category =", commons_cat)

item_labels = get_multilingual_text_field(page.text, "title")

# --- WIKIDATA PAYLOAD -----------------------

#.....
if ( len(type_q_items) > 0 ):
    type_claim        = pywikibot.Claim(repo_wikidata, _P_type)
    type_claim_target = get_Q_number(get_type(page.text))[0]
    type_claim.setTarget( type_claim_target )   #give an ItemPage as argument
#.....
institution_claim        = pywikibot.Claim(repo_wikidata, _P_institution)
#institution_Q_items = get_Q_number(get_institution(page.text))
if institution_q_item:                                
    institution_claim.setTarget( institution_q_item )   #give an ItemPage as argument

provenance_date_claim    = pywikibot.Claim(repo_wikidata, _P_start_time)
provenance_cause_claim   = pywikibot.Claim(repo_wikidata, _P_has_cause )
provenance_donator_claim = pywikibot.Claim(repo_wikidata, _P_donated_by)
if text_object_history:
    provenance_date_claim_target   = None
    if get_provenance_date(page.text):
        provenance_date_claim_target    = get_provenance_date(page.text)
        provenance_date_claim.setTarget( pywikibot.WbTime( provenance_date_claim_target) )
        #provenance_date_claim.setTarget( pywikibot.WbTime( provenance_date_claim_target, precision=provenance_date_precision ) )

    provenance_cause_claim_target   = None
    if get_provenance_cause(page.text):
        provenance_cause_claim_target   = pywikibot.ItemPage(repo_wikidata, get_provenance_cause(page.text))
        provenance_cause_claim.setTarget( provenance_cause_claim_target )
    
    provenance_donator_claim_target = None
    if get_provenance_donator(page.text) and get_Q_number(get_provenance_donator(page.text)):
        provenance_donator_claim_target = get_Q_number(get_provenance_donator(page.text))[0]
        provenance_donator_claim.setTarget( provenance_donator_claim )
    
#.....
accession_number_claim        = pywikibot.Claim(repo_wikidata, _P_accession_number)
accession_number_claim_target = get_inventory_number(page.text) 
accession_number_claim.setTarget( accession_number_claim_target )   #give a string as argument
#.....
title_claims = []
for lang in item_labels:
    title_claim        = pywikibot.Claim(repo_wikidata, _P_title)
    title_claim.setTarget ( pywikibot.WbMonolingualText( item_labels[lang], lang ) )
    title_claims.append(title_claim)
#.....
inscription_claims = []
if text_inscriptions:
    for lang in text_inscriptions:
        inscription_claim        = pywikibot.Claim(repo_wikidata, _P_inscriptions)
        inscription_claim.setTarget ( pywikibot.WbMonolingualText( text_inscriptions[lang], lang ) )
        inscription_claims.append(inscription_claim)    
#.....
image_claim        = pywikibot.Claim(repo_wikidata, _P_image)
image_claim_target = get_image_page( get_image(page.text) )
image_claim.setTarget( image_claim_target )   #give a Commons page as argument !
#.....
commons_cat_claim        = pywikibot.Claim(repo_wikidata, _P_commons_cat)
commons_cat_claim_target = commons_cat
commons_cat_claim.setTarget( commons_cat_claim_target )   #give a string as argument
#.....
location_q_items = []
if text_location:
    location_q_items = get_Q_number(text_location['en'])
    if (len(location_q_items)>0):
        location_claim        = pywikibot.Claim(repo_wikidata, _P_location)
        location_claim_target = get_Q_number(text_location['en'])[0]
        location_claim.setTarget( location_claim_target )   #give an ItemPage as argument
#.....
medium_claims = []
for medium in get_medium_Q_numbers(page.text):
    medium_claim = pywikibot.Claim(repo_wikidata, _P_medium)
    if( len(medium) == 1 ):
        medium_claim.setTarget( medium[0] )
        medium_claims.append( medium_claim )
#.....
artist_claim_target = None
if text_artist:
    artist_claim        = pywikibot.Claim(repo_wikidata, _P_artist)
    artist_claim_target = get_artist_Q_number(text_artist)
    if artist_claim_target:
        artist_claim.setTarget( artist_claim_target )   #give an ItemPage as argument
#.....
date_claim        = pywikibot.Claim(repo_wikidata, _P_date)
date_claim_target = get_date(page.text)
if date_claim_target:
    #precision=precision,. before=before, after=after,. timezone=timezone, calendarmodel=calendarmodel,. site=site
    # date_precision: https://cxuesong.github.io/WikiClientLibrary/html/47f1ea51-e5a3-894c-9615-e1af755804a5.htm
    date_precision = _epoch_dict[get_epoch(page.text)]
    date_claim.setTarget( pywikibot.WbTime( date_claim_target, precision=date_precision ) )   #give a WbTime as argument
if date_is_circa(page.text):
    qualifier = pywikibot.Claim(repo_wikidata, _P_circa)
    qualifier_target = pywikibot.ItemPage(repo_wikidata, _Q_circa)
    qualifier.setTarget(qualifier_target)
    #date_claim.addQualifier(qualifier, summary=u'Adding qualifier Circa.')
#.....
reference_claims = {}
if text_reference and (len(text_reference) > 0):
    for ref in text_reference: # text_reference is a dictionary { 'URL' : 'title'}
        ref_URL_claim = pywikibot.Claim(repo_wikidata, _P_references)
        ref_URL_claim.setTarget ( ref )
        ref_title_claim = pywikibot.Claim(repo_wikidata, _P_title)
        #TODO This is dirty, we will want to detect language automatically
        ref_title_claim.setTarget ( pywikibot.WbMonolingualText( text_reference[ref], "en" ) )
        reference_claims[ref_URL_claim] =  ref_title_claim
        
louvre_online_claim = None
if get_Louvre_online(page.text):
    louvre_online_claim = pywikibot.Claim(repo_wikidata, _P_Atlas_ID)
    louvre_online_claim.setTarget( get_Louvre_online(page.text) )
#.....
dimensions_dict = get_dimension(page.text)
unit_item = None
if dimensions_dict and ('unit' in dimensions_dict):
    unit_item = get_unit_Q_numbers(dimensions_dict['unit'])
if dimensions_dict and ('mass_unit' in dimensions_dict):
    mass_unit_item = get_unit_Q_numbers(dimensions_dict['mass_unit'])
heigth_claim = pywikibot.Claim(repo_wikidata, _P_heigth)
if dimensions_dict and ('height' in dimensions_dict):
    heigth_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['height'], unit=unit_item, error=0, site=repo_wikidata ) )
    
length_claim = pywikibot.Claim(repo_wikidata, _P_length)
if dimensions_dict and ('length' in dimensions_dict):
    length_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['length'], unit=unit_item, error=0, site=repo_wikidata ) )

width_claim = pywikibot.Claim(repo_wikidata, _P_width)
if dimensions_dict and ('width' in dimensions_dict):   
    width_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['width'], unit=unit_item, error=0, site=repo_wikidata ) )   
    
thickness_claim = pywikibot.Claim(repo_wikidata, _P_thickness)
if dimensions_dict and ('thickness' in dimensions_dict):   
    thickness_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['thickness'], unit=unit_item, error=0, site=repo_wikidata ) )
if dimensions_dict and ('depth' in dimensions_dict):   
    thickness_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['depth'], unit=unit_item, error=0, site=repo_wikidata ) )

diameter_claim = pywikibot.Claim(repo_wikidata, _P_diameter)
if dimensions_dict and ('diameter' in dimensions_dict):   
    diameter_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['diameter'], unit=unit_item, error=0, site=repo_wikidata ) )

mass_claim = pywikibot.Claim(repo_wikidata, _P_mass)
if dimensions_dict and ('mass' in dimensions_dict):   
    mass_claim.setTarget( pywikibot.WbQuantity( amount=dimensions_dict['mass'], unit=mass_unit_item, error=0, site=repo_wikidata ) )

# Scale is more complicated 
scale_claim = pywikibot.Claim(repo_wikidata, _P_scale)
if get_scale(page.text):
    scale_claim.setTarget( pywikibot.WbQuantity( amount=get_scale(page.text), error=0, site=repo_wikidata ) )

label_from_commons = commons_cat[9:].replace("_", " ")

if pollute_wikidata:
    #new_item_id = create_item(site_wikidata, item_labels)   # creates the new Wikidata item
    item_label_from_commons = {'en': label_from_commons} # Category name, without "category"
    new_item_id = create_item(site_wikidata, item_label_from_commons)
    new_item    = pywikibot.ItemPage(repo_wikidata, new_item_id)
    if (descriptions != None): new_item.editDescriptions(descriptions, summary=u'setting descriptions')
    if ( len(type_q_items) > 0 ): new_item.addClaim(type_claim, summary=u'setting Instance_of property')
    #if len(institution_Q_items) > 0: 
    if institution_q_item:                                
        new_item.addClaim(institution_claim, summary=u'setting Institution property')
    if not (accession_number_claim_target.strip() == ""):
        new_item.addClaim(accession_number_claim, summary=u'setting Inventory Number property')
    new_item.addClaim(image_claim, summary=u'setting Image property')
    if date_claim_target: new_item.addClaim(date_claim, summary=u'setting Inception property')
    if date_is_circa(page.text): date_claim.addQualifier(qualifier, summary=u'Adding qualifier Circa.')
    new_item.addClaim(commons_cat_claim, summary=u'setting Commons Category property')
    if artist_claim_target: new_item.addClaim(artist_claim, summary=u'setting Author property')
    for medium_claim in medium_claims:
        new_item.addClaim( medium_claim, summary=u'setting a Medium property')

    for reference_claim in reference_claims:
        new_item.addClaim( reference_claim, summary=u'setting a Reference_URL property')
        reference_claim.addQualifier( reference_claims[reference_claim], summary=u'Adding Title to reference.')

    if dimensions_dict:
        if 'height'    in dimensions_dict: new_item.addClaim(heigth_claim,    summary=u'setting height property')
        if 'length'    in dimensions_dict: new_item.addClaim(length_claim,    summary=u'setting length property')
        if 'width'     in dimensions_dict: new_item.addClaim(width_claim,     summary=u'setting width property')
        if 'thickness' in dimensions_dict: new_item.addClaim(thickness_claim, summary=u'setting thickness property')
        if 'diameter'  in dimensions_dict: new_item.addClaim(diameter_claim,  summary=u'setting diameter property')
        if 'mass'      in dimensions_dict: new_item.addClaim(mass_claim,      summary=u'setting mass property')
    if get_scale(page.text): new_item.addClaim(scale_claim, summary=u'setting scale property')
    if (len(location_q_items)>0): new_item.addClaim(location_claim, summary=u'setting Location property')

    if text_object_history:  
        if get_provenance_date(page.text):
            institution_claim.addQualifier( provenance_date_claim, summary=u'adding Provenance date')
        if get_provenance_cause(page.text): 
            institution_claim.addQualifier( provenance_cause_claim, summary=u'adding Provenance cause')
        if get_provenance_donator(page.text) and get_Q_number(get_provenance_donator(page.text)):
            institution_claim.addQualifier( provenance_donator_claim, summary=u'adding Donator')
    
    if len(title_claims) > 0:
        for title_claim in title_claims:
            new_item.addClaim(title_claim, summary=u'setting a Title claim')
    
    if len(inscription_claims) > 0:
        for inscription_claim in inscription_claims:
            new_item.addClaim(inscription_claim, summary=u'setting an Inscription claim')
            
    if louvre_online_claim:
        new_item.addClaim(louvre_online_claim, summary=u'setting a Atlas ID claim')

# -----------------------------------


#item = pywikibot.ItemPage.fromPage(page)
#if not item: print("NOT PRESENT ON WIKIDATA")

#print(item)
#print(dir(item))
