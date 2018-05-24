#!/usr/bin/python
import re
import requests
import lxml.html
import sys

DEBUG = True

def PrintDebug(string):
    if DEBUG:
        print(string)

def ProcessInput(argv):
    if DEBUG:
        query = "Who is the president of Italy ?"
    if len(argv) == 2:
        query = argv[1]

    PrintDebug("Query is: " + query)
    # Extract relation and entity
    matchObj = re.match(r'Who is the ([\w\s]+)* of (?:the )?([\w\s]+)*\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return {'entity': matchObj.group(2), 'relation': matchObj.group(1)}

    matchObj = re.match(r'What is the ([\w\s]+)* of (?:the )?([\w\s]+)*\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return {'entity': matchObj.group(2), 'relation': matchObj.group(1)}

    matchObj = re.match(r'When was ([\w\s]+)* born\?', query, re.I)
    if matchObj:
        if matchObj.group() == query:
            return {'entity': matchObj.group(1)}

    # No Match
    print("Could not parse input query: {}".format(query))
    raise Exception


def GetWikiLink(entity):
    entity = entity.replace(" ", "_")
    return "https://en.wikipedia.org/wiki/" + entity


def GetInfobox(wikilink):
    req = requests.get(wikilink)
    doc = lxml.html.fromstring(req.content)
    infobox = doc.xpath("//table[contains(@class,'infobox')]")
    return infobox

def GetRelationFromInfobox(infobox, relation):
    # TODO
    return


def BuildOntology(infobox):
    # TODO (Page 38 in 6_7)
    #Save ontology to file using rdflib [ontology.nt]
    return

def TranslateQueryToSparql(query):
    # TODO
    #Save query to file [sparql.q]
    return

def RunQueryOnOntology(query,ontology):
    # TODO
    return


def main(argv):
    try:
        input = ProcessInput(argv)

        PrintDebug("Parsed input is: " + input.__str__())
        wikilink = GetWikiLink(input['entity'])
        infobox = GetInfobox(wikilink)
        GetRelationFromInfobox(infobox, input['relation')
        ])
        return 0
    except:
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))