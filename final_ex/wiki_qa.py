#!/usr/bin/python
import re
import requests
import lxml.html
from lxml import etree
import sys
import rdflib

DEBUG = True

RELATION = 'relation'
ENTITY = 'entity'

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


def PrintDebug(string):
    if DEBUG:
        print(string)


def GetEntityAndRelation(matchObj):
    return {ENTITY: matchObj.group(2).replace(" ", "_"),
            RELATION: matchObj.group(1).replace(" ", "_")}


def ProcessInput(argv):
    if DEBUG:
        query = "When was rony jacobson born?"
    if len(argv) == 2:
        query = argv[1]

    PrintDebug("Query is: " + query)
    # Extract relation and entity
    matchObj = re.match(r'Who is the (\w+(?:\s\w+)*) of (?:the )?(\w+(?:\s\w+)*)\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return GetEntityAndRelation(matchObj)

    matchObj = re.match(r'What is the (\w+(?:\s\w+)*) of (?:the )?(\w+(?:\s\w+)*)\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return GetEntityAndRelation(matchObj)

    matchObj = re.match(r'When was (\w+(?:\s\w+)*) born\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return {ENTITY: matchObj.group(1).replace(" ", "_"), RELATION: 'born'}

    # No Match
    print("Could not parse input query: {}".format(query))
    raise Exception


def GetWikiLink(entity):
    return "https://en.wikipedia.org/wiki/" + entity


def GetInfoboxRelations(wikilink):
    relations = []
    requested_relation = "banana"
    # TODO
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


def BuildOntology(entity, relations):
    if DEBUG:
        relations = test_relations

    g = rdflib.Graph()
    entity_ref = rdflib.URIRef("http://example.org/" + entity.replace(" ", "_"))

    for (relation, value) in relations:
        relation_ref = rdflib.URIRef("http://example.org/" + relation.replace(" ", "_"))
        value_ref = rdflib.URIRef("http://example.org/" + value.replace(" ", "_"))
        g.add((entity_ref, relation_ref, value_ref))

    g.serialize("ontology.nt", format="nt")
    sorted(g)
    return g


def TranslateQueryToSparql(relation, entity):
    query = "select ?value where { <http://example.org/" + entity + "> <http://example.org/" + relation + "> ?value}"
    file_handler = open('query.sparql', 'w')
    file_handler.write(query)
    file_handler.close()
    return query


def RunQueryOnOntology(query, ontology):
    result = ontology.query(query)
    print(list(result))
    return


def main(argv):
    input = ProcessInput(argv)
    PrintDebug("Parsed input is: " + input.__str__())
    wikilink = GetWikiLink(input[ENTITY])
    requested_relation, relations = GetInfoboxRelations(wikilink)
    print ("Answer is: " + requested_relation)
    ontology = BuildOntology(input[ENTITY], relations)
    query = TranslateQueryToSparql(input[RELATION], input[ENTITY])
    RunQueryOnOntology(query, ontology)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
