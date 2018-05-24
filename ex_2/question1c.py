import question1a
import question1b
import sys


def main(argv):
    url_page = "https://en.wikipedia.org/wiki/Kirill_Nababkin"
    damp_val = 0.3
    if len(argv) == 3:
        url_page = argv[1]
        damp_val = argv[2]
    if len(argv) == 2:
        url_page = argv[1]

    graph_sectionA = question1a.traverse(url_page)
    rank_sectionB = question1b.page_rank(graph_sectionA, damp_val)
 
    f = open('./question1c.txt', 'w')
    f.write("Section A: {}\n\n".format(url_page))
    for url in graph_sectionA:
        f.write(url + " = { " + " , ".join(graph_sectionA[url]) + " }\n")
    f.write("Section B: {}\n\n".format(url_page))
    for url in graph_sectionA:
        f.write(url + " : " + str(rank_sectionB[url]) + "\n")
    f.close()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))