import json
import math
import pandas as pd
import re

def retrieve_corpus_infos_by_name(cli, corpus_name):
    """
    Params:
        cli : ArkindexClient
        corpus_name (str) : corpus full name in Arkindex
    
    Returns a corpus uuid in Arkindex (str) and corpus details (json)
    """
    #Retrieve corpus (project)
    corpus = cli.request('ListCorpus')
    for c in corpus:
        if c["name"] == corpus_name:
            corpus_id = c["id"]
            corpus_infos = json.dumps(c, indent=2)
            print(f"Corpus UUID is : {corpus_id}")
            return corpus_id, corpus_infos

def listelements_with_classes(cli, corpus_uuid, element_type):
    """
    Params:
        cli : ArkindexClient
        corpus_uuid (str) : corpus uuid in Arkindex
        element_type (str) : type of Arkindex element to retrieve 

    Returns a json containing a list of elements whose match the element type and with at least one class
    """
    ls_elements = []
    API_pages_count = math.ceil(int(cli.request('ListElements',corpus=corpus_uuid,type=element_type,with_classes=True)["count"])/500)
    for i in range(1,API_pages_count+1,1):
        if i == 1:
            elements = cli.request('ListElements',corpus=corpus_uuid,type=element_type,with_classes=True,page=i,page_size=500)
        else:
            elementsnext = cli.request('ListElements',corpus=corpus_uuid,type=element_type,with_classes=True,page=i,page_size=500)
            elements["results"].extend(elementsnext["results"])
    print(f'{len(elements["results"])} elements of type {element_type} with at least one class have been retrieved')
    return elements

def listelementschildren_to_df(elements):
  res = []

  for e in elements["results"]:
    rs1 = {}
    rs1["id"] = e["id"]#ID page elem dans ARkindex
    rs1["name"] = e["name"] #Page elem dans arkindex
    rs1["coords"] = e["zone"]["polygon"] #Coords
    rs1["image_id"] = e["zone"]["image"]["id"] #Id IIIF ARkindex
    rs1["image_name"] = e["zone"]["image"]["path"] #URL IIIF
    page_cote = e["zone"]["image"]["path"].replace('CADASTRE%2FETATS_DE_SECTION%2F','')
    page_cote = page_cote.replace('.jpg','')
    page_cote = page_cote.replace('.tif','')
    ls = page_cote.split('%2F')
    ls = [x for x in ls if x]
    rs1["commune"],rs1["dossier_cote"],rs1["image_cote"] = ls #Commune
    rs1["image_index"] = rs1["image_cote"][rs1["image_cote"].rfind('_')+1:]
    rs1["image_index"] = re.sub(r'^[0]+','',rs1["image_index"]) #Numéro de la page
    rs1["image_url"] = e["zone"]["url"] #URL IIIF
    rs1["image_width"] = e["zone"]["image"]["width"]
    rs1["image_height"] = e["zone"]["image"]["height"]
    res.append(rs1)
  return res

def listelements_withclass_json_to_table(elements,main_classes,special_classes,special_classes_columns):
  res = []

  for e in elements["results"]:
    rs1 = {}
    rs1["id"] = e["id"] #ID element in Arkindex
    rs1["type"] = e["type"] #Arkindex type of the element
    rs1["name"] = e["name"] #Arkindex name of the element
    rs1["coords"] = e["zone"]["polygon"] #Coordinates of the element in the image
    rs1["image_id"] = e["zone"]["image"]["id"] #Arkindex id of the IIIF image
    rs1["image_name"] = e["zone"]["image"]["path"] #IIIF url of the image (without  serveur name)
    page_cote = e["zone"]["image"]["path"].replace('CADASTRE%2FETATS_DE_SECTION%2F','') #Ajouter %2F pour les images chargées en 2022
    page_cote = page_cote.replace('.jpg','')
    page_cote = page_cote.replace('.tif','')
    rs1["commune"],rs1["dossier_cote"],rs1["image_cote"] = page_cote.split('%2F') #Commune
    rs1["image_index"] = rs1["image_cote"][rs1["image_cote"].rfind('_')+1:]
    rs1["image_index"] = re.sub(r'^[0]+','',rs1["image_index"]) #Numéro de la page
    rs1["image_url"] = e["zone"]["url"] #URL IIIF
    rs1["image_width"] = e["zone"]["image"]["width"]
    rs1["image_height"] = e["zone"]["image"]["height"]

    classes = []
    for classification in e["classifications"]:
        classes.append(classification["ml_class"]["name"])

    # Special classes
    for i in range(len(special_classes)):
        if special_classes[i] in classes:
            rs1[special_classes_columns[i]] = True
        else:
            rs1[special_classes_columns[i]] = False

    class_ = ""
    for i in range(len(main_classes)):
      if main_classes[i] in classes:
          class_ = main_classes[i]
    rs1["classe"] = class_
      
    res.append(rs1)

  df = pd.DataFrame.from_dict(res)
  return df