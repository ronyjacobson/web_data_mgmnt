import requests
import lxml.html
import xml.etree.ElementTree as ET
import sys


def main(argv):
    url_page = "https://en.wikipedia.org/wiki/Kirill_Nababkin"
    if len(argv) == 2:
        url_page = argv[1]
    
    graph = {}
    recursive_traverse(url_page, 3, graph)
    f = open('./question1c_a.txt', 'w')
    f.write("Section A: {}\n\n".format(url_page))
    for url in graph:
        f.write(url + " = { " + " , ".join(graph[url]) + " }\n")
 
    f.close()
    return 0


def traverse(url):
    graph = {}
    recursive_traverse(url, 3, graph)
    return graph


def recursive_traverse(url_page, depth, graph):
    domain = "/".join(url_page.split('/')[0:3])
 
    req = requests.get(url_page) 
    doc = lxml.html.fromstring(req.content)

    tree = ET.parse(doc)
    root = tree.getroot()
    for k in root.findall(".//img[@alt]"):
        k.attrib['alt']
     
    if url_page not in graph:
        graph[url_page] = []
 
    pointer = 0
    for point in doc.xpath("//a[starts-with(@href, '/wiki/')]"):
        if pointer >= 10:
            break
        current_url = domain + point.attrib['href']
 
        if depth > 1:
            graph[url_page].append(current_url)
        if depth == 1 and current_url in graph:
            graph[url_page].append(current_url)
        pointer += 1

    depth = depth - 1
    if depth == 0:
        return

    for url in graph[url_page]:
        if url not in graph:
            recursive_traverse(url, depth, graph)
 

if __name__ == "__main__":
    sys.exit(main(sys.argv))