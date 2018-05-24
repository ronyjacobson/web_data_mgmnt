#!/usr/bin/python
import re
import requests
import lxml.html
from lxml import etree
import sys
import rdflib

DEBUG = True

test_relations = [
    ('parent', 'orit'),
    ('parent', 'meir'),
    ('dog', 'Jullie'),
    ('dougther', 'Shirt'),
    ('spouse', 'Oron'),
    ('school', 'Nitzanim'),
    ('school', 'Ohel Shem'),
    ('born', 'July 8 1989'),
    ('eat', 'banana')]

# Consts
RELATION = 'relation'
ENTITY = 'entity'
ONTOLOGY_FILE = 'ontology.nt'
QUERY_FILE = 'query.sparql'


def print_debug(string):
    if DEBUG:
        print(string)


def get_entity_and_relation(matchObj):
    return {ENTITY: matchObj.group(2).replace(" ", "_"),
            RELATION: matchObj.group(1).replace(" ", "_")}


def process_input(argv):
    if DEBUG:
        query = "When was rony jacobson born?"
    if len(argv) == 2:
        query = argv[1]

    print_debug("Query is: " + query)
    # Extract relation and entity
    matchObj = re.match(r'Who is the (\w+(?:\s\w+)*) of (?:the )?(\w+(?:\s\w+)*)\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return get_entity_and_relation(matchObj)

    matchObj = re.match(r'What is the (\w+(?:\s\w+)*) of (?:the )?(\w+(?:\s\w+)*)\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return get_entity_and_relation(matchObj)

    matchObj = re.match(r'When was (\w+(?:\s\w+)*) born\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return {ENTITY: matchObj.group(1).replace(" ", "_"), RELATION: 'born'}

    # No Match
    print("Could not parse input query: {}".format(query))
    raise Exception


def get_wikilink(entity):
    return "https://en.wikipedia.org/wiki/" + entity


def get_infobox_relations(wikilink):
    relations = []
    requested_relation = "banana"
    # TODO - extract relation using xpath and generate a list of relation-value tuples
    '''
    req = requests.get(wikilink)
    doc = lxml.html.fromstring(req.content)
    infobox_rows = doc.xpath("//table[contains(@class,'infobox')]//tr")
    for row in infobox_rows:
        print(etree.tostring(row, pretty_print=True))
        relation = row.xpath("/tr/th/text()")
        value = row.xpath("/tr/td/text()")
        if relation and value:
            relations.append((relation, value))
    print(relations)
    '''
    return requested_relation, relations


def build_ontology(entity, relations):
    if DEBUG:
        relations = test_relations

    g = rdflib.Graph()
    entity_ref = rdflib.URIRef("http://example.org/" + entity.replace(" ", "_"))

    for (relation, value) in relations:
        relation_ref = rdflib.URIRef("http://example.org/" + relation.replace(" ", "_"))
        value_ref = rdflib.URIRef("http://example.org/" + value.replace(" ", "_"))
        g.add((entity_ref, relation_ref, value_ref))

    g.serialize(ONTOLOGY_FILE, format="nt")
    sorted(g)
    return g


def translate_query_to_sparql(relation, entity):
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
    print(list(result))
    return


def main(argv):
    input = process_input(argv)
    print_debug("Parsed input is: " + input.__str__())
    wikilink = get_wikilink(input[ENTITY])
    requested_relation, relations = get_infobox_relations(wikilink)
    print ("Answer is: " + requested_relation)
    build_ontology(input[ENTITY], relations)
    translate_query_to_sparql(input[RELATION], input[ENTITY])
    if DEBUG:
        run_query_on_ontology()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
