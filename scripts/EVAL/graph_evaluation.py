
import pandas as pd
from graphdbfunctions import select_sparql_query, convert_response_to_df
from namespaces import prefixes
import Levenshtein

def normalized_levenshtein(s1, s2):
    """
    Calculate the normalized Levenshtein similarity between two strings.
    """
    if not s1 and not s2:
        return 1.0
    elif not s1 or not s2:
        return 0.0
    else:
        distance = Levenshtein.distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1 - (distance / max_len)

def choose_named_graph(uri,query):
  """
  Choose the named graph in the SPARQL query.
  """
  new_query = query.replace("GRAPH_URI", uri)
  return new_query

def choose_property(p_,query):
  """
  Choose the property in the SPARQL query.
  """
  new_query = query.replace("PROP", p_)
  return new_query

def get_triples(query, gold_graph, pred_graph,GRAPHDB_HOST,GRAPHDB_REPO,proxies):
  """
  Get triples from the gold and predicted graphs and convert the response to a DF.
  """
  gold_query = choose_named_graph(gold_graph,query)
  gold_response = select_sparql_query(GRAPHDB_HOST,GRAPHDB_REPO,gold_query,proxies)
  gold_triples = convert_response_to_df(gold_response)

  pred_query = choose_named_graph(pred_graph,query)
  pred_response = select_sparql_query(GRAPHDB_HOST,GRAPHDB_REPO,pred_query,proxies)
  pred_triples = convert_response_to_df(pred_response)

  return gold_triples, pred_triples

def get_identical_triples(gold_df, pred_df):
  """
  Get identical triples from two DataFrames.
  This function identifies the triples that are present in both DataFrames.

  Arguments:
  gold_df -- DataFrame containing the gold standard triples
  pred_df -- DataFrame containing the predicted triples
  Returns:
  identical_triples -- DataFrame containing the identical triples
  """

  # Identify the identical triples by merging the two DataFrames on the three columns
  identical_triples = pd.merge(gold_df, pred_df, how='inner', on=['s', 'p', 'o'])
  #identical_triples = identical_triples[['s', 'p', 'o']].drop_duplicates()
  
  print(f"Number of identical triples: {len(identical_triples)}")
  
  return identical_triples

def get_non_identical_triples(gold_df, pred_df):
    """
    Get non-identical triples from two DataFrames.
    This function identifies the triples that are present in one DataFrame but not in the other.
    Arguments:
    gold_df -- DataFrame containing the gold standard triples
    pred_df -- DataFrame containing the predicted triples
    Returns:
    non_identical_gold -- DataFrame containing triples in gold_df but not in pred_df
    non_identical_pred -- DataFrame containing triples in pred_df but not in gold_df
    """
    non_identical_gold = gold_df[~gold_df.apply(tuple, 1).isin(pred_df.apply(tuple, 1))]
    non_identical_pred = pred_df[~pred_df.apply(tuple, 1).isin(gold_df.apply(tuple, 1))]

    print(f"Number of non-identical triples in gold: {len(non_identical_gold)}")
    print(f"Number of non-identical triples in pred: {len(non_identical_pred)}")
    
    return non_identical_gold, non_identical_pred

def compare_triples(gold_triples, pred_triples):
  # Compare the two DataFrames
  identical_triples = get_identical_triples(gold_triples, pred_triples)
  print(f"Number of identical triples: {len(identical_triples)}")

  # Get non-identical triples
  non_identical_gold, non_identical_pred = get_non_identical_triples(gold_triples, pred_triples)
  print(f"Number of triples in gold absent in pred: {len(non_identical_gold)}")
  print(f"Number of triples in pred absent in gold: {len(non_identical_pred)}")
  return identical_triples, non_identical_gold, non_identical_pred

def compare_dfs(gold,pred):
    #Triples of gold who are in pred
    gold_in_pred = gold[gold.apply(tuple, 1).isin(pred.apply(tuple, 1))]
    #Triples of gold who are not in pred
    gold_not_in_pred = gold[~gold.apply(tuple, 1).isin(pred.apply(tuple, 1))]
    #Triples of pred who are in gold
    pred_in_gold = pred[pred.apply(tuple, 1).isin(gold.apply(tuple, 1))]
    #Triples of pred who are not in gold
    pred_not_in_gold = pred[~pred.apply(tuple, 1).isin(gold.apply(tuple, 1))]
    return gold_in_pred, gold_not_in_pred, pred_in_gold, pred_not_in_gold

  #Now for each property, we want to see which instances one are in pred and in gold, only in gold and only in pred
def get_property_instances(df, column, property_value):
    """
    Get the instances of a property in a column of a the DataFrame.
    """
    # Filter the DataFrame for the given property
    instances = df[df[column] == property_value]
    return instances

def get_property_df(df,type_column_name='type',count_column_name='Count'):
    """
    Get the counts of each property in the DataFrame.
    """
    # Count occurrences of each property
    df = df[type_column_name].value_counts().reset_index()
    df.columns = [type_column_name, count_column_name]
    
    return df

def get_list_of_properties(df,column):
    """
    Get the list of properties in a column of a DataFrame.
    """
    # Get the unique properties in the DataFrame
    properties = df[column].unique()
    return list(properties)

def get_property_values_count_df(df,column):
    """
    Get the counts of each property in the DataFrame.
    """
    # Count occurrences of each property
    df = df[column].value_counts().reset_index()
    df.columns = [column, 'Count']
    
    return df

def compute_metrics(gold,pred):
    gold_in_pred, gold_not_in_pred, pred_in_gold, pred_not_in_gold = compare_dfs(gold, pred)
    N_Triples_gold = len(gold)
    N_Triples_pred = len(pred)
    N_Triples_gold_in_pred = len(gold_in_pred)
    N_Triples_pred_in_gold = len(pred_in_gold)
    N_Triples_gold_not_in_pred = len(gold_not_in_pred)
    N_Triples_pred_not_in_gold = len(pred_not_in_gold)

    if N_Triples_gold == 0:
        agreement_rate = 0
        deficit = 0
        recall = 0
    else:
        agreement_rate = N_Triples_gold_in_pred/N_Triples_gold
        recall = N_Triples_gold_in_pred/N_Triples_gold
        deficit = N_Triples_gold_not_in_pred/N_Triples_gold

    if N_Triples_pred == 0:
        surplus = 0
        precision = 0
    else:
        surplus = N_Triples_pred_not_in_gold/N_Triples_pred
        precision = N_Triples_gold_in_pred/N_Triples_pred

    if precision + recall == 0:
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)

    return {
        "Agreement": round(agreement_rate,4)*100,
        "Deficit": round(deficit,4)*100,
        "Surplus": round(surplus,4)*100,
        #"Precision": round(precision,4)*100,
        #"Recall": round(recall,4)*100,
        #"F1 score": round(f1_score,5)*100
    }

def df_to_latex(metrics_df):
    """
    Converts the DataFrame to LaTeX format.
    """
    #Round the values
    metrics_df["Agreement"] = metrics_df["Agreement"].round(2)
    metrics_df["Deficit"] = metrics_df["Deficit"].round(2)
    metrics_df["Surplus"] = metrics_df["Surplus"].round(2)
    #Sort by Agreement
    metrics_df.sort_values(by='Agreement', ascending=False, inplace=True)
    #Round to 2 decimal places
    metrics_df = metrics_df.round(2)
    #Convert to latex
    latex_table = metrics_df.to_latex(index=False,)
    print(latex_table)
    return latex_table