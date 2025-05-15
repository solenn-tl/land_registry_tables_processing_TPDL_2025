import bisect
import itertools
import time
import datetime
import torch
from sentence_transformers import SentenceTransformer
from collections import defaultdict, deque

embedder_name = "all-MiniLM-L6-v2" #seems that their is an issue loading large version of the model with SentenseTransformer
embedder = SentenceTransformer(embedder_name)

def query_embedding_similarity(query_ix,corpus,corpus_embeddings):
    """
    Compute the similarity between a text (string) from a "corpus of texts" (list of strings) using cosine-similarity compuded on their embeddings.
    
    Args:
        - query_ix (int) : index of an item of the corpus (used as query)
        - corpus (list of strings) : corpus
        - corpus_embeddings (list of embeddings) : list of the embeddings corresponding to the corpus items
    Returns:
        - similarity_scores (tensor) : tensor containing the similarity scores between the query's embedding and all the elements of the corpus
    """
    query_embedding = embedder.encode(corpus[query_ix], convert_to_tensor=True)
    # Cosine-similarity
    similarity_scores = embedder.similarity(query_embedding, corpus_embeddings)[0]
    return similarity_scores

def ranking_similarities(query_ix,corpus,similarity_scores,top_k='ALL'):
    """
    """
    if top_k == 'ALL':
        top_k = len(corpus)
        
    scores, indices = torch.topk(similarity_scores, k=top_k)
    
    #print("\nQuery:", corpus[query_ix])
    #print(f"Top {top_k} most similar sentences in corpus:")
    #for score, idx in zip(scores, indices):
        #print(ix, corpus[idx], f"(Score: {score:.4f})")

    return query_ix, scores, indices

def first_below_threshold(scores, threshold):
    """
    """
    # Find the first index where scores[index] < threshold
    index = bisect.bisect_right([-s for s in scores], -threshold)
    return index if index < len(scores) else -1  # Return -1 if all scores are above threshold

def compute_similarity_matrix(corpus,cosinus_similarity_treshold,top_k='ALL'):
    print(f"Embedding model : {embedder_name}")
    corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
    results = []
    for i in range(len(corpus)):
        similarity_scores = query_embedding_similarity(i,corpus,corpus_embeddings)
        query_ix, scores, indices = ranking_similarities(i,corpus,similarity_scores,top_k='ALL')
        treshold_elem_index = first_below_threshold(scores, cosinus_similarity_treshold)
        results.append([query_ix,indices[:treshold_elem_index],scores[:treshold_elem_index]])
    return results

def find_common_similarities(name_similar, firstnames_similar):
    """
    Given two lists of similar indices (name_similar and firstnames_similar),
    find the intersection for each text.
    
    Args:
    - name_similar (List[List[int]]): List of lists containing similar indices based on names.
    - firstnames_similar (List[List[int]]): List of lists containing similar indices based on firstnames.
    
    Returns:
    - List[List[int]]: List of lists containing common similar indices.
    """
    results = []
    for i in range(len(name_similar)):
        intersection = list(set(name_similar[i][1].tolist()).intersection(firstnames_similar[i][1].tolist()))
        results.append([name_similar[i][0],intersection])
    return results


def merge_lists_with_common_elements(lists):
    """
    Merges a list of lists by grouping together all lists that share 
    at least one common element.

    Each input list represents a group of related items (e.g., person mentions).
    If two or more lists have overlapping elements, they are considered connected
    and merged into a single group. The output ensures that each unique item 
    appears in only one group.

    This function works similarly to finding connected components in a graph
    where each item is a node and edges exist between items in the same list.

    Parameters:
    ----------
    lists : List[List[Hashable]]
        A list of lists, where each sublist contains elements (e.g., integers or strings)
        that represent entities or mentions. Elements must be hashable.

    Returns:
    -------
    List[List[Hashable]]
        A list of merged groups, where each group is a list of connected elements.
        Each element appears in exactly one group. The elements within each group are sorted.

    Example:
    -------
    >>> merge_lists_with_common_elements([[1, 2, 3], [3, 4], [5], [6, 7], [7, 8]])
    [[1, 2, 3, 4], [5], [6, 7, 8]]

    Notes:
    -----
    - This implementation does not require external libraries.
    - Time complexity depends on the number and size of groups, and how many elements are shared.
    """

    # Build graph of connections
    graph = defaultdict(set)
    for group in lists:
        for i in group:
            graph[i].update(group)

    visited = set()
    merged = []

    for node in graph:
        if node not in visited:
            group = set()
            queue = deque([node])
            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    group.add(current)
                    queue.extend(graph[current] - visited)
            merged.append(sorted(group))

    return merged

def remove_duplicates(list_of_lists):
    """
    """
    unique_lists = []
    seen = set()

    for lst in list_of_lists:
        tuple_lst = tuple(lst)  # Convert list to tuple (hashable)
        if tuple_lst not in seen:
            seen.add(tuple_lst)
            unique_lists.append(lst)  # Keep original list format

    return unique_lists

def export_groups(filtered_similar_items):
    """
    Retrieve all list of groups from the lists of mention index + groups.
    """
    lists = [sorted(f[1]) for f in filtered_similar_items]
    return remove_duplicates(lists)