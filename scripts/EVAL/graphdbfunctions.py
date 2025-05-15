import os
import glob
import json
import requests
import pandas as pd
import urllib.parse as up
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import RDF

def get_repositories(graphdb_host,proxies):
    """
    Get the list of repositories of a Graph DB triplestore.
    """
    url = f"{graphdb_host}/rest/repositories"
    response = requests.request("GET", url, proxies=proxies)
    print(url)
    return response

def set_default_repository(graphdb_host,repository,proxies):
    """
    Define the default repository of a Graph DB triplestore.
    """
    json_data = {
        'repository': repository,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{graphdb_host}/rest/locations/active/default-repository', headers=headers, json=json_data, proxies=proxies)
    return response

def load_ttl_files_into_named_graph(GRAPHDB_HOST,GRAPHDB_REPO,RDF_PATH,NAMED_GRAPHS_AND_RDF_FILES,proxies):
    """
    Load Turtle files in first column of NAMED_GRAPHS_AND_RDF_FILES located in folder RDF_PATH 
    into the named graphs in the NAMED_GRAPHS_AND_RDF_FILES list in a given GRAPHDB_REPO.
    """
    headers = {
        'Content-Type': 'application/x-turtle',
    }
    url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}/statements"

    for elem in NAMED_GRAPHS_AND_RDF_FILES:
        file = elem[0]
        named_graph = elem[1]
        encoded_named_graph_uri = up.quote(URIRef(named_graph).n3())

        with open(RDF_PATH + '/' + file, 'rb') as f:
            data = f.read()

        final_url = url + "?context=" + encoded_named_graph_uri
        response = requests.post(final_url, headers=headers, data=data, proxies=proxies)
        print(response.text)

def remove_named_graphs(GRAPHDB_HOST,GRAPHDB_REPO,NAMED_GRAPHS,proxies):
    """
    Delete named graphs of a given list from a given GRAPHDB_REPO.
    """
    
    headers = {
        'Content-Type': 'application/x-turtle',
    }

    url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}/statements"

    for g in NAMED_GRAPHS:
        final_url = url + "?context=" + up.quote(URIRef(g).n3())
        response = requests.request("DELETE", final_url, headers=headers, proxies=proxies)
        response

def update_sparql_query(GRAPHDB_HOST,GRAPHDB_REPO,QUERY,proxies):
  url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}/statements"
  query_encoded = up.quote(QUERY)
  response = requests.request("POST", url, data=f"update={query_encoded}", headers={'Content-Type': 'application/x-www-form-urlencoded'}, proxies=proxies)
  print(response, response.text)

def select_sparql_query(GRAPHDB_HOST, GRAPHDB_REPO, QUERY, proxies):
    url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}"
    query_encoded = up.urlencode({"query": QUERY})
    headers = {'Accept': 'application/sparql-results+json'}  # Get JSON-formatted results
    
    response = requests.get(f"{url}?{query_encoded}", headers=headers, proxies=proxies)
    
    if response.status_code == 200:
        return response
    else:
        print(f"Query failed with status code {response.status_code}")
        print(response.text)
        return None

def convert_response_to_df(response):
    results = response.json()["results"]["bindings"]
    rows = []
    for result in results:
        row = {var: result[var]["value"] for var in result}
        rows.append(row)
    return pd.DataFrame(rows)

def sparql_response_to_rdf_graph(response):
    graph = Graph()
    results = response.json()["results"]["bindings"]
    for result in results:
        # Assuming variables are 's', 'p', 'o' for subject, predicate, object
        s = URIRef(result["s"]["value"]) if "s" in result else BNode()
        p = URIRef(result["p"]["value"])
        o = URIRef(result["o"]["value"]) if "o" in result else Literal(result["o"]["value"])
        graph.add((s, p, o))
    return graph

def resolve_blank(graph, node, visited=None):
    """ Recursively follow blank nodes to a final non-blank node. """
    if visited is None:
        visited = set()
    
    if not isinstance(node, BNode):
        return node  # Already a literal or URI
    
    if node in visited:
        return node  # Prevent infinite loops

    visited.add(node)
    for p, o in graph.predicate_objects(node):
        if not isinstance(o, BNode):
            return o
        return resolve_blank(graph, o, visited)
    
    return node  # Fallback if no outgoing edges

def normalize_triple(graph, triple):
    """ Normalize a triple by resolving blank nodes. """
    s, p, o = triple
    s_resolved = resolve_blank(graph, s) if isinstance(s, BNode) else s
    o_resolved = resolve_blank(graph, o) if isinstance(o, BNode) else o
    return (s_resolved, p, o_resolved)

def normalize_graph(graph):
    """ Normalize all triples in the graph. """
    norm_triples = set()
    for triple in graph:
        norm_triples.add(normalize_triple(graph, triple))
    return norm_triples

def compare_graphs(graph1, graph2):
    norm_graph1 = normalize_graph(graph1)
    norm_graph2 = normalize_graph(graph2)
    
    # Find the intersection (matching triples)
    matching_triples = norm_graph1 & norm_graph2
    print(f"Matching triples: {len(matching_triples)}")
    
    return matching_triples