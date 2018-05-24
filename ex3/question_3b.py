import rdflib

graph = rdflib.Graph()
graph.parse("question3Aontology.txt", format="nt")

file_handler = open('question3Bontology.txt', 'a+')

query1 = "select ?player ?team where { ?player <http://example.org/birthPlace> ?city . ?player <http://example.org/playsFor> ?team . ?city <http://example.org/located_in> <http://example.org/Spain> . ?team <http://example.org/league> <http://example.org/Premier_League>}"
result1 = graph.query(query1)

file_handler.write("Result section a:\n")
for tup in list(result1):
    file_handler.write(str(tup) + "\n")

query2 = "select ?player ?team where { ?player <http://example.org/birthDate> ?originaldate . BIND(xsd:dateTime(CONCAT(REPLACE(str(?originaldate), 'http://example.org/', ''), 'T00:00:00')) AS ?date). FILTER (?date > '1990-01-01T00:00:00'^^xsd:dateTime) . ?player <http://example.org/playsFor> ?team }"
result2 = graph.query(query2)

file_handler.write("Result section b:\n")
for tup in list(result2):
    file_handler.write(str(tup) + "\n")

query3 = "select ?player where { ?player <http://example.org/birthPlace> ?birthCity . ?player <http://example.org/playsFor> ?team . ?team <http://example.org/homeCity> ?homeCity . FILTER(SAMETERM(?birthCity,?homeCity))}"
result3 = graph.query(query3)

file_handler.write("Result section c:\n")
for tup in list(result3):
    file_handler.write(str(tup) + "\n")

query4 = "select ?team1 ?team2 where { ?team1 <http://example.org/homeCity> ?homeCity1 . ?team2 <http://example.org/homeCity> ?homeCity2 . FILTER(!SAMETERM(?team1, ?team2) && SAMETERM(?homeCity1,?homeCity2))}"
result4 = graph.query(query4)

# deleting dups
lst = list(result4)
res = []
for tup in lst:
    if tup[0] < tup[1]:
        res.append(tup)

file_handler.write("Result section d:\n")
for tup in res:
    file_handler.write(str(tup) + "\n")
