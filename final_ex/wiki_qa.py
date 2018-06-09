#!/usr/bin/python
import re
import requests
import lxml.html
from lxml import etree
import sys
import rdflib
from collections import defaultdict
import numpy as np

DEBUG = False
DEBUG_QUERIES = True

# Consts
RELATION = 'relation'
ENTITY = 'entity'
ONTOLOGY_FILE = 'ontology.nt'
QUERY_FILE = 'query.sparql'


debug_queries = [
    "Who is the president of Italy?",
    "Who is the spouse of Gal Gadot?",
    "What is the alma mater of Gal Gadot?",
    "Who is the MVP of the 2011 NBA Finals?",
    "What is the best picture of the 90th Academy Awards?",
    "What is the capital of Canada?",
    "What is the capital of Argentina?",
    "What is the Largest city of Italy?",
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
    raise Exception("Error: Could not parse input query: [{}]".format(query))


def get_wikilink(entity):
    return "https://en.wikipedia.org/wiki/" + entity

def parse_info(relation, values):
    parsed_values = []

    parsed_relation = re.sub(r"[^\w\s]", "", relation)

    for value in values:
        parsed_value = value
        if "capital" in relation.lower():
            parsed_value = re.sub(r" \d.*", "", parsed_value)
        if relation.lower() != "Time zone".lower():
            # Remove ()
            parsed_value = re.sub(r"\(.*\)", "", parsed_value)
        # Remove []
        parsed_value = re.sub(r"\[.*\]", "", parsed_value).strip()
        parsed_values.append(parsed_value)

    return parsed_relation, parsed_values

def get_infobox_relations(wikilink):
    ''' The function receives a wikilink, fetches it's contents and extracts all relations in the infobox'''
    relations = defaultdict(list)

    req = requests.get(wikilink)
    doc = lxml.html.fromstring(req.content)
    infobox_rows = doc.xpath("//table[contains(@class,'infobox') and position()=1]/tr")

    for row in infobox_rows:
        extracted_values = []
        relation = ''.join(row.xpath("./th//text()")).replace('\n', ' ').strip().encode('utf-8')

        # Check if there are multiple values (a list)
        values = row.xpath("./td//li")
        if len(values) == 0:
            value = ''.join(row.xpath("./td//text()")).replace('\n', ' ').strip().encode('utf-8')

            if relation != '' and value != '':
                extracted_values.append(value)
        else:
            for xml_value in values:
                value = ''.join(xml_value.xpath(".//text()")).replace('\n', ' ').strip().encode('utf-8')
                if relation != '' and value != '':
                    extracted_values.append(value)

        parsed_relation, extracted_values = parse_info(relation, extracted_values)
        relations[parsed_relation] = extracted_values


    if DEBUG:
        print("relations:")
        for relation in relations:
            for value in relations[relation]:
                print("{} : {}".format(relation, value))

    if len(relations) == 0:
        raise Exception("Error: Could not find relations for wikilink: [{}]".format(wikilink))

    return relations


def levenshtein_distance(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in xrange(size_x):
        matrix [x, 0] = x
    for y in xrange(size_y):
        matrix [0, y] = y

    for x in xrange(1, size_x):
        for y in xrange(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

def extract_query_answer(relations, query_relation):
    ''' Take the closest relation to the one asked in the query using Jaccard word distance and return it's value and
    it's name as it will be in in the ontology. '''
    min_word_distance = float('inf')
    requested_relation_answers = []
    relation_name = ""

    for relation in relations.keys():
        # Compare only alpha numeric characters
        clean_relation = re.sub(r'[^a-zA-Z123456789\s]', "", relation.lower())
        clean_query_relation = re.sub(r'[^a-zA-Z123456789\s]', "", query_relation.lower())

        relation_word_distance = levenshtein_distance(clean_relation, clean_query_relation)

        if (clean_query_relation == 'capital'):
            if ('capital' in clean_relation):
                relation_word_distance = 0

        if (clean_query_relation == 'largest city'):
            if ('largest city' in clean_relation):
                relation_word_distance = 0

        # print "distance {}<-->{} is {}".format(clean_query_relation, clean_relation, relation_word_distance)
        if relation_word_distance < min_word_distance:
            requested_relation_answers = relations[relation]
            relation_name = relation
            min_word_distance = relation_word_distance
    return requested_relation_answers, relation_name


def build_ontology(entity, relations):
    g = rdflib.Graph()
    entity_ref = rdflib.URIRef("http://example.org/{}".format(entity.replace(" ", "_")))

    for relation in relations:
        relation_ref = rdflib.URIRef("http://example.org/{}".format(relation.replace(" ", "_")))
        for value in relations[relation]:
            value_ref = rdflib.URIRef("http://example.org/{}".format(value.replace(" ", "_")))
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
    print ("Query: {}\nWikipedia's value/s for {} relation is: {}".format(query, relation_name, answers))
    build_ontology(input[ENTITY], relations)
    translate_query_to_sparql(relation_name, input[ENTITY])
    if DEBUG:
        run_query_on_ontology()
    return 0


def main(argv):
    if DEBUG_QUERIES:
        for query in debug_queries:
            wiki_qa_main(query)
            print ("*************************************")

    query = ""
    if len(argv) == 2:
        query = argv[1]
    if query == "":
        print("Error: There was no given query.")
        return 1
    wiki_qa_main(query)
    # try:
    #     wiki_qa_main(query)
    # except Exception as error:
    #     print(error)



if __name__ == "__main__":
    sys.exit(main(sys.argv))
