import torch
import re
import sys
import os
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
import Levenshtein as lev

# Access to the utils directory
current_dir = os.getcwd()
utils_dir = os.path.join(current_dir, '..', 'utils')
sys.path.append(utils_dir)

from string_utils import NormalizeText

class LinkingUtils:
    
    @staticmethod
    def index_to_uri(row_index, uri_col_idx, labels_uri_tab):
        """
        Using the index of an entity in a table (list of lists), retrieve its uri in the same list of lists
        """
        uri = labels_uri_tab[row_index][uri_col_idx]
        return uri
        
    @staticmethod
    def associate_matches_with_values(queries, matching_results, candidates_uris, col_uris_index):
        """
        Using the results of a matching function, return a list of lists using original query and one or many associated uris. If no match for a value, return 'NIL'
        """
        final_results = {}
        assert len(queries) == len(matching_results)
        for i in range(len(queries)):
            elem = matching_results[i]
            query_results = []
            for concept in elem:
                if concept[0] != 1000000:
                    uri = LinkingUtils.index_to_uri(concept[0], col_uris_index, candidates_uris)
                    query_results.append(uri)
                else:
                    query_results.append('NIL')
            final_results[queries[i]] = query_results
        return final_results

    @staticmethod
    def normalized_levenshtein(str1, str2):
        """Returns a normalized Levenshtein distance (1 - distance)"""
        if len(str1) == 0 and len(str2) == 0:
            return 1.0  # Both empty, consider them identical
        if len(str1) == 0 or len(str2) == 0:
            return 0.0  # One is empty, completely dissimilar
        return 1 - lev.distance(str1, str2) / max(len(str1), len(str2))

    @staticmethod
    def cluster_by_embeddings_similarity(texts, threshold):
        model = SentenceTransformer("all-MiniLM-L6-v2")
        if len(texts) == 0:
            return []

        embeddings = model.encode(texts, convert_to_numpy=True)
        sim_matrix = cosine_similarity(embeddings)

        visited = set()
        groups = []

        for i in range(len(texts)):
            if i in visited:
                continue
            group = [i]
            visited.add(i)
            for j in range(i + 1, len(texts)):
                if j not in visited and sim_matrix[i][j] >= threshold:
                    group.append(j)
                    visited.add(j)
            groups.append(group)
        return groups
    
class EditDistanceBasedSimilarity:
    """
    A class for performing entity linking using edit distance similarity (fuzzy matching).
    """
    
    @staticmethod
    def get_top_k_similar(query, candidates, remove_chars_regex, replacement_char, top_k=3, threshold=0.7):
        """
        Compare a query string to a list of candidate strings and return the top-k most similar ones above a similarity threshold.
        
        :param query: The string to compare.
        :param candidates: A list of strings to compare against.
        :param remove_chars_regex: A regex pattern to remove unwanted characters.
        :param replacement_char: The character used to replace removed characters.
        :param top_k: The number of top similar items to return.
        :param threshold: The minimum similarity ratio to consider.
        :return: A list of tuples (index, candidate, similarity_score) sorted by highest similarity.
        """
        query, crossed_out = NormalizeText.separate_crossed_out(query)
        
        # Normalize query
        normalized_query = NormalizeText.trim_whitespace(NormalizeText.replace_characters(
            NormalizeText.remove_accents(query.lower()), remove_chars_regex, replacement_char
        ))
        
        # Normalize candidates
        normalized_candidates = [
            NormalizeText.replace_characters(NormalizeText.remove_accents(c.lower()), remove_chars_regex, replacement_char)
            for c in candidates
        ]
        
        # Compute similarity scores
        similarities = [(i, candidates[i], SequenceMatcher(None, normalized_query, norm_cand).ratio()) 
                        for i, norm_cand in enumerate(normalized_candidates)]
        
        # Filter by threshold and sort by similarity in descending order
        filtered_sorted = sorted(
            [(index, cand, score) for index, cand, score in similarities if score >= threshold],
            key=lambda x: x[2], reverse=True
        )
        
        # Return top-k results
        return filtered_sorted[:top_k]
        
    @staticmethod
    def EL_gestaltpatternmatching(queries, candidates, remove_chars_regex, replacement_char, split_chars, top_k=1, threshold=0.7):
        """
        Execute entity linking task using gestalt pattern matching. If match are under a certain treshold, return a NIL entity.
        """
        results = []
        print(f'Queries : {queries}')
        print()
        for query in queries:
            # Normalize query
            query, crossed_out = NormalizeText.separate_crossed_out(query)
            normalized_query = NormalizeText.trim_whitespace(NormalizeText.replace_characters(
                NormalizeText.clean_arrow_texts(NormalizeText.remove_accents(query.lower())), remove_chars_regex, replacement_char
            ).replace('  ',' '))
            print(f"Query {query} normalized as {normalized_query}")
            res = EditDistanceBasedSimilarity.get_top_k_similar(query, candidates, remove_chars_regex, replacement_char, top_k=1, threshold=0.7)
            print(f"Step 1 results : {res}")
            
            if len(res) == 0:
                print('NEXT')
                updated_query = NormalizeText.remove_conjunctions_prepositions_nltk(normalized_query)
                subqueries = NormalizeText.split_text(updated_query, split_chars)
                print(f'Try to match subqueries {subqueries}')
                subres = []
                for subquery in subqueries:
                    subquery = NormalizeText.trim_whitespace(subquery)
                    res2 = EditDistanceBasedSimilarity.get_top_k_similar(subquery, candidates, remove_chars_regex, replacement_char, top_k=1, threshold=0.7)
                    if len(res2) > 0:
                        subres.append(res2[0])
                if len(subres) > 0:
                    print(f"Step 2 results : {subres}")
                    results.append(subres)
                else:
                    results.append([(1000000,'NIL',0.0)])
            else:
                results.append(res)
        return results

class EmbeddingSimilarity:
    """
    A class for computing similarity between text embeddings using cosine similarity,
    ranking similarities, and performing entity linking through embedding-based matching.
    """
    
    @staticmethod
    def embedding_similarity(query, candidates_embeddings, embedder, remove_chars_regex, replacement_char):
        """
        Compute the similarity between a text query and a corpus using cosine similarity.
        
        Args:
            query (str): Query text.
            candidates_embeddings (list of tensors): List of embeddings corresponding to corpus items.
            embedder (SentenceTransformer): Pre-trained embedding model.
        
        Returns:
            torch.Tensor: Tensor containing similarity scores between query embedding and corpus.
        """
        query, crossed_out = NormalizeText.separate_crossed_out(query)
        normalized_query = NormalizeText.replace_characters(
            NormalizeText.remove_accents(query.lower()), remove_chars_regex, replacement_char
        )
        
        query_embedding = embedder.encode(normalized_query, convert_to_tensor=True)
        similarities = embedder.similarity(query_embedding, candidates_embeddings)[0]
        
        return similarities
    
    @staticmethod
    def get_top_k_similar(query, candidates, similarity_scores, threshold, top_k):
        """
        Rank and retrieve top-k most similar items from the corpus based on similarity scores.
        
        Args:
            query (str): Query text.
            candidates (list of str): List of corpus items.
            similarity_scores (torch.Tensor): Similarity scores for the corpus.
            top_k (int or str, optional): Number of top matches to retrieve. Defaults to 'ALL'.
            verbose (bool, optional): If True, prints the ranking results. Defaults to False.
        
        Returns:
            tuple: Query, indices of top matches, similarity scores of top matches.
        """
        scores, indices = torch.topk(similarity_scores, k=top_k)
        indices = indices.tolist()
        scores = scores.tolist()

        res = []
        print("\nQuery:", query)
        print(f"Top {top_k} most similar concepts:")
        for score, idx in zip(scores, indices):
            res.append((idx, candidates[idx],score))
            print(idx, candidates[idx], f"(Score: {score:.4f})")

        filtered_sorted = sorted(
            [(index, cand, score) for index, cand, score in res if score >= threshold],
            key=lambda x: x[2], reverse=True
        )
        
        return filtered_sorted
    
    @staticmethod
    def EL_embedding_cosinedistance_matching(queries, candidates, embedder, remove_chars_regex, replacement_char, split_chars, top_k=1, threshold=0.8):
        """
        Perform entity linking by matching queries to corpus entities based on similarity scores.
        
        Args:
            queries (list of str): List of query strings.
            candidates (list of str): List of entity labels.
            embedder (SentenceTransformer): Pre-trained embedding model.
            min (float): Minimum threshold for matching.
            remove_chars_regex (str): 
            replacement_char (str): Regex pattern for characters to replace with whitespace.
            split_chars (str): Regex pattern for splitting text into words
            top_k (int): 
            threshold (float):
        
        Returns:
            list: Matching results containing entity matches or NIL if no match is found.
        """
        candidates_embeddings = embedder.encode(candidates, convert_to_tensor=True)
        results = []
        print(f'Queries : {queries}')
        print()
        for query in queries:
            # Normalize query
            query, crossed_out = NormalizeText.separate_crossed_out(query)
            normalized_query = NormalizeText.replace_characters(
                NormalizeText.clean_arrow_texts(NormalizeText.remove_accents(query.lower())), remove_chars_regex, replacement_char
            )
            print(f"Query {query} normalized as {normalized_query}")

            similarity_scores = EmbeddingSimilarity.embedding_similarity(normalized_query, candidates_embeddings, embedder, remove_chars_regex, replacement_char)
            res = EmbeddingSimilarity.get_top_k_similar(normalized_query, candidates, similarity_scores, threshold, top_k)

            print(f"Step 1 results : {res}")
            
            if len(res) == 0:
                print('NEXT')
                updated_query = NormalizeText.remove_conjunctions_prepositions_nltk(normalized_query)
                subqueries = NormalizeText.split_text(updated_query, split_chars)
                print(f'Try to match subqueries {subqueries}')
                subres = []
                for subquery in subqueries:
                    similarity_scores = EmbeddingSimilarity.embedding_similarity(subquery, candidates_embeddings, embedder, remove_chars_regex, replacement_char)
                    res2 = EmbeddingSimilarity.get_top_k_similar(subquery, candidates, similarity_scores, threshold, top_k)
                    if len(res2) > 0:
                        subres.append(res2[0])
                if len(subres) > 0:
                    print(f"Step 2 results : {res2}")
                    results.append(subres)
                else:
                    results.append([(1000000,'NIL',0.0)])
            else:
                results.append(res)
        return results

class PrepareQueriesForEL:

    @staticmethod
    def retrieve_mentions(jsons_list, jsons_dir, column_name, has_named_entities):
        """
        For each document of a collection, return its uuid, its_sub elements. Adaptated if there are named_entities or not.
        """
        mentions = []
        for JSON in jsons_list:
            with open(JSON) as f:
                page = json.load(f)
            page_uuid = JSON.replace(jsons_dir,"").replace('.json','')
            #Retrieve all the taxpayers text of the page
            mentions_by_page = []
            counter = 0 #Index of the line in the page
            for line in page["entities"]:
                keys = list(line.keys())
                row = []
                if has_named_entities and column_name in keys:
                    row = [page_uuid, counter, line[column_name]['interpreted_text'],line[column_name]['ner_interpreted_text_grouped']]
                elif has_named_entities and column_name not in keys:
                    row = [page_uuid, counter, "MISSING", {"name":"MISSING","firstnames":"","birthname":"","activity":[],"address":[],"title":[],"familystatus":[]}]
                elif has_named_entities == False and column_name in keys:
                    row = [page_uuid, counter, line[column_name]['interpreted_text']]
                elif has_named_entities == False and column_name not in keys:
                    row = [page_uuid, counter, "MISSING"]
                counter += 1
                #Treat the special case of taxpayer index number (which is optionnal)
                if has_named_entities and column_name == "Ⓒ" and column_name in keys and 'Ⓖ' in keys:
                    row[3]["index_num"] = line["Ⓖ"]["interpreted_text"]
                elif has_named_entities and column_name == "Ⓒ" and column_name in keys and 'Ⓖ' not in keys:
                    row[3]["index_num"] = "MSSING"
                elif has_named_entities and column_name not in keys:
                    row[3]["index_num"] = "MSSING"
                mentions_by_page.append(row)

            mentions.append(mentions_by_page)
        return mentions

    @staticmethod
    def distinct_mentions_without_ne(mentions):
        """
        For a list of mentions with named entities inside, returns the list of distinct mentions (without duplicated values).
        """
        distinct_mentions = []
        for page in mentions:
            for line in page:
                if line[2] not in distinct_mentions:
                    distinct_mentions.append(line[2])
        return distinct_mentions

    @staticmethod
    def distinct_mentions_with_ne(mentions):
        """
        For a list of mentions with named entities inside, returns the list of distinct mentions (without duplicated values) and a dictionnary 
        with mentions as key and named entities dict as value (specific to land registry).
        """
        distinct_mentions = []
        distinct_mentions_details = {}
        for page in mentions:
            for line in page:
                if line[2] not in distinct_mentions:
                    distinct_mentions.append(line[2])
                    distinct_mentions_details.update({line[2]:line[3]})
        return distinct_mentions, distinct_mentions_details

class MentionGrouper:
    """
    A class two perform Taxpayer mention linking and grouping including post-merging or splitting strategy
    """
    def __init__(self, name_threshold=0.85, firstname_threshold=0.85, familystatus_threshold=0.8, post_merge_threshold=0.7, mesure="normalizedlevenshtein", model_name="all-MiniLM-L6-v2"):
        self.name_threshold = name_threshold
        self.firstname_threshold = firstname_threshold
        self.familystatus_threshold = familystatus_threshold
        self.mesure = mesure
        self.model_name = model_name

    # Load the embedding model (not used if normalized levenstein)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    def normalized_levenshtein(self, str1, str2):
        """Returns a normalized Levenshtein distance (1 - distance)"""
        if len(str1) == 0 and len(str2) == 0:
            return 1.0  # Both empty, consider them identical
        if len(str1) == 0 or len(str2) == 0:
            return 0.0  # One is empty, completely dissimilar
        return 1 - lev.distance(str1, str2) / max(len(str1), len(str2))

    def cluster_by_levenshtein(self, texts, threshold):
        if len(texts) == 0:
            return []

        sim_matrix = np.zeros((len(texts), len(texts)))

        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = LinkingUtils.normalized_levenshtein(texts[i], texts[j])
                sim_matrix[i][j] = sim_matrix[j][i] = sim

        visited = set()
        groups = []

        for i in range(len(texts)):
            if i in visited:
                continue
            group = [i]
            visited.add(i)
            for j in range(i + 1, len(texts)):
                if j not in visited and sim_matrix[i][j] >= threshold:
                    group.append(j)
                    visited.add(j)
            groups.append(group)

        return groups

    def cluster_by_sequence_matcher(self, texts, threshold):
        if len(texts) == 0:
            return []
    
        # Create a similarity matrix using SequenceMatcher
        sim_matrix = np.zeros((len(texts), len(texts)))
    
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = SequenceMatcher(None, texts[i], texts[j]).ratio()  # Similarity score between 0 and 1
                sim_matrix[i][j] = sim_matrix[j][i] = sim
    
        visited = set()
        groups = []
    
        # Group texts based on the similarity matrix
        for i in range(len(texts)):
            if i in visited:
                continue
            group = [i]
            visited.add(i)
            for j in range(i + 1, len(texts)):
                if j not in visited and sim_matrix[i][j] >= threshold:
                    group.append(j)
                    visited.add(j)
            groups.append(group)
    
        return groups

    def cluster_by_embeddings_similarity(self, texts, threshold):
        if len(texts) == 0:
            return []

        embeddings = model.encode(texts, convert_to_numpy=True)
        sim_matrix = cosine_similarity(embeddings)

        visited = set()
        groups = []

        for i in range(len(texts)):
            if i in visited:
                continue
            group = [i]
            visited.add(i)
            for j in range(i + 1, len(texts)):
                if j not in visited and sim_matrix[i][j] >= threshold:
                    group.append(j)
                    visited.add(j)
            groups.append(group)
        return groups

    def get_first_token(self, name):
        return name.strip().split()[0].lower() if name.strip() else ""

    def is_similar(self, s1, s2, threshold):
        if not s1 or not s2:
            return False
        return LinkingUtils.normalized_levenshtein(s1.lower(), s2.lower()) >= threshold

    # Helper method to compute similarity using SequenceMatcher
    def sequence_matcher_similarity(self, a, b):
        # Return a normalized similarity score between 0 and 1
        return SequenceMatcher(None, a, b).ratio()
    
    def group_mentions(self, mentions):
        ################ STEP 1 ################
        # Retrieve the number of taxpayers mentions
        indices = list(range(len(mentions)))
        # Get the list of names
        names = [m['name'] for m in mentions]
        
        # Compute name similarity and create first-level groups based on the chosen similarity measure
        if self.mesure == "embeddingcosinus":
            name_groups = self.cluster_by_embeddings_similarity(names, self.name_threshold)
        elif self.mesure == "normalizedlevenshtein":
            name_groups = self.cluster_by_levenshtein(names, self.name_threshold)
        elif self.mesure == "sequencematcher":
            name_groups = self.cluster_by_sequence_matcher(names, self.name_threshold)
        
        final_groups = []
        
        ################ STEP 2 ################
        # Refine the groups using first names
        for name_group in name_groups:
            # Get mentions corresponding to the current name group
            name_group_mentions = [mentions[i] for i in name_group]
            # Extract first names from these mentions
            firstnames_raw = [m.get('firstnames', '') for m in name_group_mentions]
        
            # Identify indices of non-empty first names
            non_empty_indices = [i for i, fn in enumerate(firstnames_raw) if fn.strip()]
            non_empty_firstnames = [firstnames_raw[i] for i in non_empty_indices]
        
            # If there are no non-empty first names, create a single subgroup
            if len(non_empty_firstnames) == 0:
                firstname_subgroups = [list(range(len(name_group)))]
            else:
                # Cluster non-empty first names based on the chosen similarity measure
                if self.mesure == "embeddingcosinus":
                    fn_clusters = self.cluster_by_embeddings_similarity(non_empty_firstnames, self.firstname_threshold)
                elif self.mesure == "normalizedlevenshtein":
                    fn_clusters = self.cluster_by_levenshtein(non_empty_firstnames, self.firstname_threshold)
                elif self.mesure == "sequencematcher":
                    fn_clusters = self.cluster_by_sequence_matcher(non_empty_firstnames, self.firstname_threshold)
        
                firstname_subgroups = []
                # Map clustered first names back to their original indices within the name group
                for cluster in fn_clusters:
                    mapped = [non_empty_indices[i] for i in cluster]
                    firstname_subgroups.append(mapped)
        
                # Handle mentions with empty first names by creating separate subgroups
                empty_indices = [i for i in range(len(name_group)) if i not in sum(firstname_subgroups, [])]
                for ei in empty_indices:
                    firstname_subgroups.append([ei])
        
            for subgrp in firstname_subgroups:
                subgroup_indices = [name_group[i] for i in subgrp]
        
                # Create a mapping of family statuses to mentions
                status_map = {}
                for idx in subgroup_indices:
                    status = mentions[idx].get("familystatus")
                    if status:
                        status_map.setdefault(status, []).append(idx)
                    else:
                        status_map.setdefault(None, []).append(idx)
        
                status_keys = [s for s in status_map if s is not None]
        
                # If there is more than one unique family status, cluster the statuses
                if len(status_keys) <= 1:
                    final_groups.append(subgroup_indices)
                else:
                    if self.mesure == "embeddingcosinus":
                        status_groups = self.cluster_by_embeddings_similarity(status_keys, self.familystatus_threshold)
                    elif self.mesure == "normalizedlevenshtein":
                        status_groups = self.cluster_by_levenshtein(status_keys, self.familystatus_threshold)
                    elif self.mesure == "sequencematcher":
                        status_groups = self.cluster_by_sequence_matcher(status_keys, self.familystatus_threshold)
        
                    grouped_indices = []
                    for group in status_groups:
                        group_statuses = [status_keys[i] for i in group]
                        group_indices = []
                        for s in group_statuses:
                            group_indices.extend(status_map[s])
                        grouped_indices.append(group_indices)
        
                    # Handle mentions with no family status
                    if None in status_map:
                        if len(grouped_indices) == 1:
                            grouped_indices[0].extend(status_map[None])
                        else:
                            grouped_indices.append(status_map[None])
        
                    final_groups.extend(grouped_indices)
        
        # --- POST MERGE: based on NAME + first token of FIRSTNAMES + same INDEX_NUM ---
        merged = []
        while final_groups:
            base = final_groups.pop(0)
            base_mentions = [mentions[i] for i in base]
            base_name = base_mentions[0]['name']
            base_firstnames = base_mentions[0].get('firstnames', '').split()
            base_index = base_mentions[0].get('index_num')
        
            to_merge = [base]
        
            i = 0
            while i < len(final_groups):
                comp = final_groups[i]
                comp_mentions = [mentions[j] for j in comp]
                comp_name = comp_mentions[0]['name']
                comp_firstnames = comp_mentions[0].get('firstnames', '').split()
                comp_index = comp_mentions[0].get('index_num')
        
                # Check similarity of names
                if self.mesure == "sequencematcher" and self.sequence_matcher_similarity(base_name, comp_name) < self.name_threshold:
                    i += 1
                    continue
                elif not self.is_similar(base_name, comp_name, self.name_threshold):
                    i += 1
                    continue
        
                # Compare first names token by token
                merge_flag = True
                for b_fn, c_fn in zip(base_firstnames, comp_firstnames):
                    if self.mesure == "sequencematcher" and self.sequence_matcher_similarity(b_fn, c_fn) < self.firstname_threshold:
                        merge_flag = False
                        break
                    elif not self.is_similar(b_fn, c_fn, self.firstname_threshold):
                        merge_flag = False
                        break
        
                # If index numbers are the same, merge regardless of first name differences
                if base_index and comp_index and str(base_index) == str(comp_index):
                    to_merge.append(comp)
                    final_groups.pop(i)
                    continue
                # If first names are similar and index numbers are different, do not merge
                elif merge_flag and (not base_index or not comp_index):
                    to_merge.append(comp)
                    final_groups.pop(i)
                    continue
        
                i += 1
        
            merged_group = sum(to_merge, [])
            merged.append(merged_group)
        
        return merged