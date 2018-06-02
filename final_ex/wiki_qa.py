#!/usr/bin/python
import re
import requests
import lxml.html
from lxml import etree
import sys
import rdflib
import distance

DEBUG = True

test_relations = [
    ('parent', 'orit'),
    ('parent', 'meir'),
    ('dog', 'Jullie'),
    ('dougther', 'Shirt'),
    ('spouse', 'Oron'),
    ('school', 'Nitzanim'),
    ('school', 'Ohel Shem'),
    ('Born', 'July 8 1989'),
    ('eat', 'banana')]

# Consts
RELATION = 'relation'
ENTITY = 'entity'
ONTOLOGY_FILE = 'ontology.nt'
QUERY_FILE = 'query.sparql'


queries = [
    "Who is the president of Italy?",
    "Who is the spouse of Gal Gadot?",
    "What is the alma mater of Gal Gadot?",
    "Who is the MVP of the 2011 NBA Finals?",
    "What is the best picture of the 90th Academy Awards?",
    "What is the capital of Canada?",
    "When was Theodor Herzl born?",
    "Who is the parent of Barack Obama?"
]

def print_debug(string):
    if DEBUG:
        print(string)


def get_entity_and_relation(matchObj):
    return {ENTITY: matchObj.group(2).strip(),
            RELATION: matchObj.group(1).strip()}


def process_input(query):

    print_debug("Query is: " + query)
    # Extract relation and entity
    matchObj = re.match(r'Who is the (.*) of (?:the )?(.*)\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return get_entity_and_relation(matchObj)

    matchObj = re.match(r'What is the (.*) of (?:the )?(.*)\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return get_entity_and_relation(matchObj)

    matchObj = re.match(r'When was (.*) Born\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return {ENTITY: matchObj.group(1).strip(), RELATION: 'Born'}

    # No Match
    print("Error: Could not parse input query: [{}]".format(query))
    raise Exception


def get_wikilink(entity):
    return "https://en.wikipedia.org/wiki/" + entity


def get_infobox_relations(wikilink):
    ''' The function receives a wikilink, fetches it's contents and extracts all relations in the infobox'''
    relations = []

    TH_XPATH = "//table[contains(@class,'infobox')]/tr[{}]/th//text()"
    TD_XPATH = "//table[contains(@class,'infobox')]/tr[{}]/td//text()"

    req = requests.get(wikilink)
    doc = lxml.html.fromstring(req.content)
    infobox_rows = doc.xpath("//table[contains(@class,'infobox')]/tr")
    for i in range(0, len(infobox_rows)):
        relation = ''.join(doc.xpath(TH_XPATH.format(i))).replace('\n', ' ').strip().encode('utf-8')
        value = ''.join(doc.xpath(TD_XPATH.format(i))).replace('\n', ' ').strip().encode('utf-8')
        if relation != '' and value != '':
            relations.append([relation, value])
    if DEBUG:
        print("relations:")
        for relation, value in relations:
            print "{} : {}".format(relation, value)

    return relations


def extract_query_answer(relations, query_relation):
    ''' Take the closest relation to the one asked in the query using Jaccard word distance and return it's value and
    it's name as it will be in in the ontology. '''
    min_word_distance = float('inf')
    requested_relation_answer = ""
    relation_name = ""

    for relation, value in relations:
        relation_word_distance = distance.jaccard(relation.lower(), query_relation.lower())
        if relation_word_distance < min_word_distance:
            requested_relation_answer = value
            relation_name = relation
            min_word_distance = relation_word_distance
    return requested_relation_answer, relation_name


def build_ontology(entity, relations):
    if DEBUG:
        relations = relations  # test_relations

    g = rdflib.Graph()
    entity_ref = rdflib.URIRef("http://example.org/" + entity.replace(" ", "_"))

    for relation, value in relations:
        relation_ref = rdflib.URIRef("http://example.org/" + relation.replace(" ", "_"))
        value_ref = rdflib.URIRef("http://example.org/" + value.replace(" ", "_"))
        g.add((entity_ref, relation_ref, value_ref))

    g.serialize(ONTOLOGY_FILE, format="nt")
    sorted(g)
    return g


def translate_query_to_sparql(relation, entity):
    entity = entity.replace(' ', '_')
    relation = relation.replace(' ', '_')
    query = "select ?value where { <http://example.org/" + entity + "> <http://example.org/" + relation + "> ?value}"
    file_handler = open(QUERY_FILE, 'w')
    file_handler.write(query)
    file_handler.flush()
    file_handler.close()
    return query


def run_query_on_ontology():
    query = open(QUERY_FILE, 'r').readline()
    graph = rdflib.Graph()
    file = open(ONTOLOGY_FILE, 'r')
    graph.parse(file, format='nt')
    result = graph.query(query)
    print("SPARQL reault: {}".format(list(result)))
    return


def wiki_qa_main(query):
    try:
        input = process_input(query)
        print_debug("Parsed input is: " + input.__str__())
        wikilink = get_wikilink(input[ENTITY].replace(" ", "_"))
        relations = get_infobox_relations(wikilink)
        answer, relation_name = extract_query_answer(relations, input[RELATION])
        print ("Answer is: " + answer)
        build_ontology(input[ENTITY], relations)
        translate_query_to_sparql(relation_name, input[ENTITY])
        if DEBUG:
            run_query_on_ontology()
        return 0
    except:
        return 1


def main(argv):
    if DEBUG:
        for query in queries:
            wiki_qa_main(query)
            print ("*************************************")

    query = ""
    if len(argv) == 2:
        query = argv[1]
    if query == "":
        print "Error: There was no given query."
        return 1

    return wiki_qa_main(query)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
