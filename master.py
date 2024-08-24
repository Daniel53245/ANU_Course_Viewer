from core import course
from core import worm
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, URIRef
from rdflib.namespace import RDF


def merge_course_to_graph(course_list):
    graph = Graph()
    for course in course_list:
        triples = course.to_rdf()
        for triple in triples:
            graph.add(triple)
    return graph


def plot_rdf_graph(rdf_graph):
    """
    Plots an RDF graph using NetworkX and Matplotlib.

    Parameters:
    - rdf_graph: An rdflib.Graph object containing the RDF data.
    """
    # Create a directed graph from RDF data
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    # if the realtion is ex.prequusite_from\
    # ex = Namespace("http://caligula.today/onto#")
    # RDF.tyep
    for s, p, o in rdf_graph:
        if p == URIRef("http://caligula.today/onto#prequisite_from"):
            G.add_node(s, label=s.split("/")[-1])
            G.add_node(o, label=o.split("/")[-1])
            G.add_edge(s, o, label="requires")
        if p == RDF.type:
            G.add_node(s, label=s.split("/")[-1])
    # Set up the plot
    plt.figure(figsize=(12, 8))

    # Layout for the graph
    pos = nx.circular_layout(G)  # You can change the layout algorithm here

    # Draw the graph
    labels = nx.get_node_attributes(G, "label")
    nx.draw(
        G,
        pos,
        labels=labels,
        with_labels=True,
        node_size=200,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
        edge_color="gray",
    )
    nx.draw_networkx_edges(G, pos, edge_color="gray", width=1.5, alpha=0.7)

    # Show the plot
    plt.title("RDF Graph Visualization")
    plt.savefig("output.png")


if __name__ == "__main__":
    target = input("Enter the course URL in ANU programme and course page:\n")
    print("Processing the course page")
    # Creta the crawl objec
    crawler = worm.BasicCrawler(target, max_depth=2)
    if not crawler._is_course_page(target):
        print("The URL is not a course page")
        exit(-1)
    crawler.crawl()
    course_list = crawler.crawled_courses
    #  Linke the courses
    course_list = crawler.crawled_courses
    for elem in course_list:
        for preq_code in elem.prequisites:
            for course in course_list:
                if course.course_code == preq_code:
                    elem.prequiste_course[preq_code] = course
                    break
    # Generate rdf graph
    merge_course_to_graph(course_list).serialize("output.ttl", format="turtle")
    # Display the graph
    print("Displaying the graph")
    plt.savefig("output.png")
    print("Done")
