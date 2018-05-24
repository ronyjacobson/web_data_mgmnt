import question1a
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
    rank = page_rank(graph_sectionA, damp_val)

    f = open('./question1c_b.txt', 'w')
    f.write("Section B: {}\n\n".format(url_page))
    for url in graph_sectionA:
        f.write(url + " : " + str(rank[url]) + "\n")

    f.close()
    return 0


def page_rank(graph, damping_value):
    rank = {}
    graph_length = len(graph)
    init_rank = float(1)/graph_length

    for url in graph:
        rank[url] = {}

        rank[url]["in_edges"] = []

        graph_length_at_url = len(graph[url])
        if graph_length_at_url == 0:
            rank[url]["out_edges"] = 1
            rank[url]["in_edges"].append(url)
        else:
            rank[url]["out_edges"] = graph_length_at_url

        rank[url]["rank"] = [init_rank, init_rank]
        
    for url in graph:
        for out_url in graph[url]:
            rank[out_url]["in_edges"].append(url)

    damping_rank = damping_value * init_rank
    for i in range(0, 100):
        for url in rank:
            in_amount = 0
            for in_edge in rank[url]["in_edges"]:
                in_amount += rank[in_edge]["rank"][(i-1) % 2] / rank[in_edge]["out_edges"]
            rank[url]["rank"][i % 2] = damping_rank + (1-damping_value)*in_amount
 
    ret_page_rank = {}
    for url in graph:
        ret_page_rank[url] = rank[url]["rank"][0]
 
    return ret_page_rank
 
 
if __name__ == "__main__":
    sys.exit(main(sys.argv))