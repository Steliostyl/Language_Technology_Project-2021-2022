import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from thefuzz import fuzz

#cc_categories = ['CD', 'CC', 'DT', 'EX', 'IN', 'LS', 'MD', 'PDT',
#'POS', 'PRP', 'PRP$', 'RP', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB']

oc_categories = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'NN', 'NNS',
'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'FW']

def pos_tag(articles):
    """PoS Tag articles"""

    pos_tags = {}
    for article in articles:
        # Split article paragraphs into sentences
        tokenized = sent_tokenize(article['paragraphs'])
        # Send the tokenized words of each sentence for PoS tagging
        pos_tag = process_content(tokenized)
        # Add the tags of each sentence to the pos tags list
        pos_tags[article['url']] = pos_tag
    return pos_tags, filter_stop_words(pos_tags)

def process_content(tokenized):
    """Tokenize each word of the
    input (tokenized) sentence"""

    try:
        tagged = []
        # PoS tag every tokenized sentence
        for sent in tokenized:
            words = word_tokenize(sent)
            tagged.append(nltk.pos_tag(words))
        return(tagged)

    except Exception as ex:
        print(str(ex))

def get_wordnet_pos(tag):
    """Convert nltk pos_tags to wordnet pos tags"""
    proper_tag = [tag][0][0][0]
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(proper_tag, wordnet.NOUN)

def filter_stop_words(pos_tags):
    """Filter stop words from pos tags,
    lemmatize them and create lemmas dictionary"""

    pos_no_stopwords = {}   
    lemmas = {}
    articles_w_count = {}
    lemmatizer = WordNetLemmatizer()
    
    # article[0] -> article url
    # article[1] -> article tags
    for article in pos_tags.items():
        article_pos_no_sw = []
        article_w_count = 0
        for sent in article[1]:
            filtered_pos = []
            for tag in sent:
                # Filter words that have not
                # been tagged with a closed 
                # category tag
                if tag[1] not in oc_categories:
                    continue

                # Filter unwanted symbols
                if len(tag[0]) == 1:
                    utf_8_bytes = bytes(tag[0], 'utf-8')
                    temp = []
                    for byte in utf_8_bytes:
                        temp.append(byte)
                    #                    Numbers                      Capital Letters                    Small Letters
                    if temp[0] not in range(48, 58) and temp[0] not in range(64, 91) and temp[0] not in range(97, 123):
                        continue

                # Add tag to filtered_pos
                article_w_count += 1
                filtered_pos.append(tag)
                lemma = lemmatizer.lemmatize(tag[0], pos= get_wordnet_pos(tag[1])).lower()

                # If lemma doesn't already exist 
                # in the lemmas dict, create it
                # and set the count for the 
                # corresponding article to 1
                if lemma not in lemmas.keys():
                    lemmas[lemma] = {
                        article[0]: 1
                    }
                # If lemma has already been added
                # to the dict
                else:
                    # If lemma has previously been found in 
                    # the same article, increase its count
                    if article[0] in lemmas[lemma].keys():
                        lemmas[lemma][article[0]] += 1
                    # Otherwise, create a new entry for this
                    # article and initialize its count to 1
                    else:
                        lemmas[lemma][article[0]] = 1
            article_pos_no_sw.append(filtered_pos)
        articles_w_count[article[0]] = article_w_count
        pos_no_stopwords[article[0]] = article_pos_no_sw

    return pos_no_stopwords, articles_w_count, lemmas

def dict_sort(dict):
    """Sort a dictionary by its values (and not the keys).
    Used in the query function, where we want the articles of the answer
    to be sorted according to their weight sum."""
    
    # Sort answer documents by weight
    sorted_dict = {}
    sorted_keys = sorted(dict, key=dict.get, reverse=True)
    for key in sorted_keys:
        sorted_dict[key] = dict[key]
    return sorted_dict   

def nltk_query(lemmas, query):
    """Query function that takes as input the lemmas dict as well as a query
    (which can be one or multiple words) and returns the articles in which
    the query word(s) can be found, sorted by their weight sums."""

    lemmatizer = WordNetLemmatizer()
    answer = {}
    articles_containing_query = []

    # Split the query into words and search for them in the articles
    for word in query.split():
        # Try finding answer by directly looking for query word in the dictionary keys. 
        if word in lemmas:
            articles_containing_query = lemmas[word].items() 
        # If this doesn't work, try finding answer by lemmatizing query words.
        else:
            token = nltk.tag.pos_tag([word])[0]
            qword_lemma = lemmatizer.lemmatize(token[0], pos= get_wordnet_pos(token[1]))
            if qword_lemma in lemmas:
                articles_containing_query = lemmas[qword_lemma].items()
            # If this doesn't work either, try finding answer using string matching
            else:
                for lemmas_key, lemmas_value in lemmas.items():
                    ratio = fuzz.ratio(qword_lemma, lemmas_key)
                    if ratio > 90:
                        articles_containing_query.append(lemmas_value.items())
                        #print('Similarity between the words ', word, '(', qword_lemma, ') and ', lemmas_key, ': ', ratio)
        
        # Add the weight of the word in each article to the answer[article] 
        # so that if multiple words of a single query are found in the 
        # same articles their weights get summed
        for article, weight in articles_containing_query:
                if article in answer:
                    answer[article] += weight
                else:
                    answer[article] = weight

    # Answer not found by lemmatizing OR string matching
    if len(answer.keys()) == 0:
        return {query :'Not found'}
                    
    return dict_sort(answer)