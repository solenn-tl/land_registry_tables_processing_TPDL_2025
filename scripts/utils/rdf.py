import os
import uuid
import pandas as pd
import numpy as np
import csv
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SKOS

class skosConceptUtil:
    def __init__(self):
        # Initialize the RDF graph
        self.graph = Graph()
        # Define common namespaces
        self.ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
        self.CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
        self.SOURCE = Namespace("http://rdf.geohistoricaldata.org/id/source/")
        self.TAXPAYER = Namespace("http://rdf.geohistoricaldata.org/id/taxpayer/")
        self.NATURE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/plotNature/")
        self.graph.bind("addr", self.ADDR)
        self.graph.bind("cad", self.CAD)
        self.graph.bind("source", self.SOURCE)
        self.graph.bind("taxpayer", self.TAXPAYER)
        self.graph.bind("pnature", self.NATURE)

    def detect_voc_lang(column_name):
        """
        Parse a column name to detect vocabulary, property name and value lang
        """
        if "@" in column_name and ':' in column_name:
            name, lang = column_name.split('@')
            voc, name = name.split(':')
            return voc, name, lang
        elif "@" in column_name and ':' not in column_name:
            name, lang = column_name.split('@')
            return '', name, lang
        elif "@" not in column_name and ':' in column_name:
            voc, name = column_name.split(':')
            return voc, name, ''

    def init_nature_concepts_from_csv(self, nature_csv, output_dir):
        """
        Taking a CSV with a defined structure, create a Turtle file describing plot natures.
        """
        skos_natures = pd.read_csv(nature_csv, header=0)
        columns = list(skos_natures.columns)
        # Iterate over each row in the DataFrame
        for index, row in skos_natures.iterrows():
            subject_uri = URIRef(f"{self.NATURE}{str(row['skos:Concept'])}")
            self.graph.add((subject_uri, RDF.type, self.CAD.Nature))
            self.graph.add((subject_uri, RDF.type, SKOS.Concept))
            self.graph.add((subject_uri, SKOS.inScheme, URIRef(f"{self.CAD}{str(row['skos:inScheme'])}")))

            if not pd.isnull(row['skos:broader']):
                if ',' in row["skos:broader"]:
                    for broader in row["skos:broader"].split(','):
                        self.graph.add((subject_uri, SKOS.broader, URIRef(f"{self.NATURE}{str(broader)}")))
                else:
                    self.graph.add((subject_uri, SKOS.broader, URIRef(f"{self.NATURE}{str(row['skos:broader'])}")))

            if not pd.isnull(row['skos:closeMatch']):
                if ',' in row["skos:closeMatch"]:
                    for cm in row["skos:closeMatch"].split(','):
                        self.graph.add((subject_uri, SKOS.closeMatch, URIRef(f"{self.NATURE}{str(cm)}")))
                else:
                    self.graph.add((subject_uri, SKOS.closeMatch, URIRef(f"{self.NATURE}{str(row['skos:closeMatch'])}")))
                    
            if not pd.isnull(row['skos:exactMatch']):
                if ',' in row["skos:exactMatch"]:
                    for em in row["skos:exactMatch"].split(','):
                        self.graph.add((subject_uri, SKOS.exactMatch, URIRef(f"{self.NATURE}{str(em)}")))
                else:
                    self.graph.add((subject_uri, SKOS.exactMatch, URIRef(f"{self.NATURE}{str(row['skos:exactMatch'])}")))

            if not pd.isnull(row['skos:prefLabel@fr']):
                self.graph.add((subject_uri, SKOS.prefLabel, Literal(row["skos:prefLabel@fr"],lang='fr')))

            if not pd.isnull(row['skos:altLabel@fr']):
                if ',' in row["skos:altLabel@fr"]:
                    altlabels = row["skos:altLabel@fr"].replace(', ',',').split(',')
                    for altLabel in altlabels:
                        self.graph.add((subject_uri, SKOS.altLabel, Literal(altLabel,lang='fr')))
                else:
                    self.graph.add((subject_uri, SKOS.altLabel, Literal(row['skos:altLabel@fr'],lang='fr')))

            if not pd.isnull(row['skos:hiddenLabel@fr']):
                if ',' in row["skos:hiddenLabel@fr"]:
                    hiddenlabels = row["skos:hiddenLabel@fr"].replace(', ',',').split(',')
                    for hiddenLabel in hiddenlabels:
                        self.graph.add((subject_uri, SKOS.hiddenLabel, Literal(hiddenLabel,lang='fr')))
                else:
                    self.graph.add((subject_uri, SKOS.hiddenLabel, Literal(row['skos:hiddenLabel@fr'],lang='fr')))
                    
            if row["skos:prefLabel@en"] == row["skos:prefLabel@en"]:
                self.graph.add((subject_uri, SKOS.prefLabel, Literal(row["skos:prefLabel@en"],lang='en')))
        
            if not pd.isnull(row['skos:altLabel@en']):
                if ',' in row["skos:altLabel@en"]:
                    altlabels = row["skos:altLabel@en"].replace(', ',',').split(',')
                    for altLabel in altlabels:
                        self.graph.add((subject_uri, SKOS.altLabel, Literal(altLabel,lang='en')))
                else:
                    self.graph.add((subject_uri, SKOS.altLabel, Literal(row['skos:altLabel@en'],lang='en')))
        
            if not pd.isnull(row["rdfs:comment@fr"]):
                self.graph.add((subject_uri, RDFS.comment, Literal(row["rdfs:comment@fr"],lang='fr')))
        
            if not pd.isnull(row["cad:TFNBGroup"]):
                tfnbgroup = str(row["cad:TFNBGroup"])
                if ',' in tfnbgroup:
                    tfnbgroup = str(tfnbgroup).replace(', ',',').split(',')
                    for elem in tfnbgroup:
                        self.graph.add((subject_uri, self.CAD.TFNBGroup, Literal(elem)))
        
        # Print out the graph in Turtle syntax
        output_path = os.path.join(output_dir,'natures.ttl')
        self.graph.serialize(destination=output_path, format='turtle')
        

class CreateRDFUtil:
    def __init__(self):
        # Initialize the RDF graph
        self.graph = Graph()
        # Define common namespaces
        self.ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
        self.CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
        self.SOURCE = Namespace("http://rdf.geohistoricaldata.org/id/source/")
        self.TAXPAYER = Namespace("http://rdf.geohistoricaldata.org/id/taxpayer/")
        self.graph.bind("addr", self.ADDR)
        self.graph.bind("cad", self.CAD)
        self.graph.bind("source", self.SOURCE)
        self.graph.bind("taxpayer", self.TAXPAYER)


    def add_taxpayer_entities(self, taxpayer_json, element_uuid:str):
        """
        Convert a taxpayer JSON feature to RDF and add it to the graph. Can contain one to many taxpayers

        :param taxpayer_json: Dictionary containing person data
        Example: {
            "name"
            "firstnames"
            "address"
            "activity"
            "title"
            "familystatus"
            "birthname"
        }
        """
        counter = 1
        for taxpayer in taxpayer_json["entities_json"]["taxpayers"]:
            person_uri = URIRef(self.TAXPAYER[taxpayer_json["element_uuid"] + '_taxpayer_' + str(counter)])
            self.graph.add((person_uri, RDF.type, self.CAD.Taxpayer))
            
            #RDFS Label
            if len(taxpayer_json['name']) > 0 and len(taxpayer_json['firstnames']) > 0:
                self.graph.add((person_uri, RDFS.label, Literal(taxpayer_json['name'] + ' ' + taxpayer_json['firstnames'])))
            else:
                self.graph.add((person_uri, RDFS.label, Literal(taxpayer_json['name'])))
                
            #Taxpayer properties
            if len(taxpayer_json['name']) > 0:
                self.graph.add((person_uri, self.CAD.taxpayerLabel, Literal(taxpayer_json['name'])))
            if len(taxpayer_json['firstnames']) > 0:
                self.graph.add((person_uri, self.CAD.taxpayerFirstName, Literal(taxpayer_json['firstnames'])))
            if len(taxpayer_json['activity']) > 0:
                for elem in taxpayer_json['activity']:
                    self.graph.add((person_uri, self.CAD.taxpayerActivity, Literal(elem)))
            if len(taxpayer_json['address']) > 0:
                for elem in taxpayer_json['address']:
                    self.graph.add((person_uri, self.CAD.taxpayerAddress, Literal(elem)))
            if len(taxpayer_json['title']) > 0:
                for elem in taxpayer_json['title']:
                    self.graph.add((person_uri, self.CAD.taxpayerTitle, Literal(elem)))
            if len(taxpayer_json['familystatus']) > 0:
                for elem in taxpayer_json['familystatus']:
                    self.graph.add((person_uri, self.CAD.taxpayerStatus, Literal(elem)))
            if len(taxpayer_json['birthname']) > 0:
                self.graph.add((person_uri, self.CAD.taxpayerBirthname, Literal(taxpayer_json['birthname'])))
    
            #Source
            self.graph.add((person_uri, self.CAD.fromSource, URIRef(self.SOURCE[element_uuid])))
            counter += 1