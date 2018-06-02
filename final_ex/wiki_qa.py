#!/usr/bin/python
import re
import requests
import lxml.html
from lxml import etree
import sys
import rdflib
import distance
from collections import defaultdict

DEBUG = True

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
    relations = defaultdict(list)

    TH_XPATH = "//table[position()=1 and contains(@class,'infobox')]/tr[{}]/th//text()"
    TD_LI_XPATH = "//table[position()=1 and contains(@class,'infobox')]/tr[{}]/td//li[{}]//text()"
    TD_XPATH = "//table[position()=1 and contains(@class,'infobox')]/tr[{}]/td//text()"

    req = requests.get(wikilink)
    doc = lxml.html.fromstring(req.content)
    infobox_rows = doc.xpath("//table[contains(@class,'infobox')]/tr")
    for i in range(1, len(infobox_rows)+1):
        relation = ''.join(doc.xpath(TH_XPATH.format(i))).replace('\n', ' ').strip().encode('utf-8')

        # Check if there are multiple values (a list)
        values = doc.xpath("//table[position()=1 and contains(@class,'infobox')]/tr[{}]/td//li".format(i))
        if len(values) == 0:
            value = ''.join(doc.xpath(TD_XPATH.format(i))).replace('\n', ' ').strip().encode('utf-8')
            if relation != '' and value != '':
                relations[relation].append(value)
        else:
            for j in range(1, len(values)+1):
                value = ''.join(doc.xpath(TD_LI_XPATH.format(i,j))).replace('\n', ' ').strip().encode('utf-8')
                if relation != '' and value != '':
                    relations[relation].append(value)

    if DEBUG:
        print("relations:")
        for relation in relations:
            print "{} : {}".format(relation, relations[relation])

    return relations


def extract_query_answer(relations, query_relation):
    ''' Take the closest relation to the one asked in the query using Jaccard word distance and return it's value and
    it's name as it will be in in the ontology. '''
    min_word_distance = float('inf')
    requested_relation_answers = []
    relation_name = ""

    for relation in relations.keys():
        relation_word_distance = distance.levenshtein(relation.lower(), query_relation.lower())
        if relation_word_distance < min_word_distance:
            requested_relation_answers = relations[relation]
            relation_name = relation
            min_word_distance = relation_word_distance
    return requested_relation_answers, relation_name


def build_ontology(entity, relations):
    g = rdflib.Graph()
    entity_ref = rdflib.URIRef("http://example.org/" + entity.replace(" ", "_"))

    for relation in relations:
        relation_ref = rdflib.URIRef("http://example.org/" + relation.replace(" ", "_"))
        for value in relations[relation]:
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
    input = process_input(query)
    print_debug("Parsed input is: " + input.__str__())
    wikilink = get_wikilink(input[ENTITY].replace(" ", "_"))
    relations = get_infobox_relations(wikilink)
    answers, relation_name = extract_query_answer(relations, input[RELATION])
    print ("Answer is: {}".format(answers))
    build_ontology(input[ENTITY], relations)
    translate_query_to_sparql(relation_name, input[ENTITY])
    if DEBUG:
        run_query_on_ontology()
    return 0


def main(argv):
    if DEBUG:
        for query in queries:
            wiki_qa_main(query)
            print ("*************************************")

    query = ""
    if len(argv) == 2:
        query = argv[1]
    if query == "":
        print("Error: There was no given query.")
        return 1

    return wiki_qa_main(query)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
