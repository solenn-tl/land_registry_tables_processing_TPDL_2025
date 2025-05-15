import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np
import itertools
import Levenshtein

embedder_name = "all-MiniLM-L6-v2"
embedder = SentenceTransformer(embedder_name)
#"dangvantuan/sentence-camembert-base"

def compute_statistics_by_prop(cluster, prop_value_ix):
    """
    Compute intra-cluster similarity statistics (mean, median, std) for embeddings cosine similarity and edit distance similarity.
    """
    names = [row[prop_value_ix] + " " +  row[prop_value_ix + 1] for row in cluster]

    if len(names) < 2:
        return None  # No statistics if there's only one item in the cluster

    # Compute embeddings
    embeddings = embedder.encode(names, convert_to_tensor=True)
    
    # Compute pairwise similarities
    embedding_similarities = []
    edit_distances = []
    
    for name1, name2 in itertools.combinations(names, 2):
        # Cosine similarity for embeddings
        sim = util.pytorch_cos_sim(embedder.encode(name1, convert_to_tensor=True), 
                                   embedder.encode(name2, convert_to_tensor=True))
        embedding_similarities.append(sim.item())

        # Edit distance normalized (Levenshtein distance / max_length)
        edit_distance = Levenshtein.distance(name1, name2) / max(len(name1), len(name2))
        edit_distances.append(1 - edit_distance)  # Convert to similarity

    # Compute statistics
    stats = {
        "Cosinus Similarity Mean (emb)": np.mean(embedding_similarities),
        "Cosinus Similarity Median (emb)": np.median(embedding_similarities),
        "Cosinus Similarity Std (emb)": np.std(embedding_similarities),
        "Levenshtein Similarity Mean (str)": np.mean(edit_distances),
        "Levenshtein Similarity Median (str)": np.median(edit_distances),
        "Levenshtein Similarity Std (str)": np.std(edit_distances),
    }

    return stats