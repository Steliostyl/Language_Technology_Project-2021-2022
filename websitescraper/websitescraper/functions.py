import json
from xml.dom import minidom
import math
import xml.etree.ElementTree as ET
import random

def readJSON(filename):
    """Read articles from JSON file"""

    with open(filename, 'r') as file:
        articles = json.load(file)
    return articles

def saveDictToJSON(input_Dict, filename):
    """Write article list to JSON file"""

    # Open the file with filename in w (write) mode
    # If it already exists, it gets overwritten
    with open(filename, 'w') as file:
        json.dump(input_Dict, file, indent=2, default=str)
    file.close()

def calculateTFidf(lemmas, article_w_count):
    """Calculate weights for all lemmas (using tf_idf)"""
    
    article_count = len(article_w_count)
    for lemma in lemmas:
        # IDF of each lemma is equal to the base 2 log of the
        # article count of our database devided by the count
        # of articles the lemma is present in
        idf = math.log2(article_count/len(lemmas[lemma].keys()))
        for key in lemmas[lemma].keys():
            tf = lemmas[lemma][key]/article_w_count[key]
            tf_idf = tf*idf
            lemmas[lemma][key] = tf_idf

    return lemmas

def createXML(lemmas_dict):
    """Create and save XML file from lemmas dict"""

    root = minidom.Document()
    inv_index = root.createElement('inverted_index')
    root.appendChild(inv_index)

    for word in lemmas_dict.keys():
        new_lemma = root.createElement('lemma')
        new_lemma.setAttribute('name', word)
        for key in lemmas_dict[word].keys():
            new_document = root.createElement('document')
            new_document.setAttribute('url', str(key))
            new_document.setAttribute('weight', str(lemmas_dict[word][key]))
            new_lemma.appendChild(new_document)
        inv_index.appendChild(new_lemma)

    xml_str = root.toprettyxml(indent ='\t')
    
    with open('lemmas.xml', "w", encoding='utf-8') as file:
        file.write(xml_str) 

def readXML(filename):
    """Read XML file containing lemmas and load it to a dict"""

    lemma_dict = {}
    root_node = ET.parse(filename).getroot()
    # Get all lemmas
    for lemma in root_node.findall('lemma'):
        lemma_name = lemma.get('name')
        docs = {}
        for document in lemma.findall('document'):
            url = document.get('url')
            weight = document.get('weight')
            docs[url] = weight
        
        lemma_dict[lemma_name] = docs
        
    return lemma_dict

def generateRandomQueries(lemmas):
    """Generate random queries"""

    # Create queries
    lemmaKeys = list(lemmas.keys())
    # 20 1-word queries
    queries = random.sample(lemmaKeys, 20)
    # 20 2-word queries
    for i in range(0,20):
        queries.append(' '.join(random.sample(lemmaKeys, 2)))
    # 30-triple word queries
    for i in range(0,30):
        queries.append(' '.join(random.sample(lemmaKeys, 3)))
    # 30-quad word queries
    for i in range(0,30):
        queries.append(' '.join(random.sample(lemmaKeys, 4)))
    return queries