from rdflib import Graph, URIRef, Literal, RDFS, Namespace, BNode
from rdflib.namespace import SKOS, RDF, RDFS, DCTERMS, XSD
import uuid

def arkindex_class_to_skosconcept(classe):
    if classe == "ets_tab_p1":
        return "ETSTabP1"
    elif classe == "ets_couv":
        return "ETSCover"

def ets_type(tag):
    if tag == "AV_1822_NB" or tag == "AV_1822_B" or tag =="AV_1822":
        return "EtatsDeSections_Av_1822"
    elif tag == "AP_1822":
        return "EtatsDeSections_Ap_1822"
    else:
        return "EtatsDeSections_Scp_Seine_1835"

def generate_rdf_resource_section_landmark(rdf_entities, DEP, COMMUNE):
    """
    Create rdf resources of type ADDR:Landmark, addr:isLandmarkType cad_ltype:Section using covers informations and additionnal metadata
    """
    g = Graph()
    ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
    CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
    LANDMARK = Namespace("http://rdf.geohistoricaldata.org/id/landmark/")
    SOURCE = Namespace("http://rdf.geohistoricaldata.org/id/source/")
    CAD_LTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/")
    LRTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/landmarkRelationType/")
    LR = Namespace("http://rdf.geohistoricaldata.org/id/landmarkRelation/")
    g.bind("addr", ADDR)
    g.bind("cad", CAD)
    g.bind("landmark", LANDMARK)
    g.bind("cad_ltype", CAD_LTYPE)
    g.bind("landmarkRelation",LR)
    g.bind("lrype", LRTYPE)
    g.bind("source", SOURCE)

    uris_dict = {}
    
    for rdf_entity in rdf_entities:
        if rdf_entity["uuid"] not in ["missing", 'Ø', None, '']:
            uri = URIRef(LANDMARK + rdf_entity["uuid"])
            g.add((uri, RDF.type, ADDR.Landmark))
            g.add((uri, ADDR.isLandmarkType, URIRef(CAD_LTYPE + rdf_entity["cad_ltype"])))
            g.add((uri, DCTERMS.identifier, Literal(rdf_entity["identifier"])))
            g.add((uri, RDFS.label, Literal(rdf_entity["label"])))
            g.add((uri, SKOS.prefLabel, Literal(rdf_entity["label"])))
            g.add((uri, SKOS.prefLabel, Literal(rdf_entity["label"])))
            g.add((uri, ADDR.hasTrace, URIRef(SOURCE + rdf_entity["source_uuid"])))

            #uri_lr = URIRef(BNode().n3())
            p1 = uri.replace("http://rdf.geohistoricaldata.org/id/landmark/","")
            uri_lr = URIRef(LR + p1 + '_' + DEP + '_' + COMMUNE)
            g.add((uri_lr, RDF.type, ADDR.LandmarkRelation))
            g.add((uri_lr, ADDR.isLandmarkRelationType, LRTYPE.Within))
            g.add((uri_lr, ADDR.locatum, uri))
            g.add((uri_lr, ADDR.relatum, URIRef(LANDMARK + DEP + '_' + COMMUNE)))

        uris_dict[rdf_entity["label"]] = str(uri)

    return g, uris_dict

def generate_rdf_resource_commune_landmark(g, rdf_entity):
    """
    Add a commune rdf resources into an existing graph.
    """
    ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
    CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
    LANDMARK = Namespace("http://rdf.geohistoricaldata.org/id/landmark/")
    CAD_LTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/")
    
    uri_comm = URIRef((LANDMARK + rdf_entity["departement_num"] + "_" + rdf_entity["commune_code"]))
    g.add((uri_comm, RDF.type, ADDR.Landmark))
    g.add((uri_comm, RDFS.label, Literal(rdf_entity["label"])))
    g.add((uri_comm, DCTERMS.identifier, Literal(rdf_entity["commune_code"])))
    g.add((uri_comm, ADDR.isLandmarkType, CAD_LTYPE.Commune))


def generate_source_rdf_resource(rdf_entities):
    """
    Create rdf resources of type SOURCE (Page et Registre)
    """
    g = Graph()
    ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
    CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
    SOURCE = Namespace("http://rdf.geohistoricaldata.org/id/source/")
    SRCTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/")
    MLCLASSE =  Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/mlClasse/")
    RICO = Namespace("https://www.ica.org/standards/RiC/ontology#")
    TIME = Namespace("http://www.w3.org/2006/time#")
    
    g.bind("addr", ADDR)
    g.bind("cad", CAD)
    g.bind("source", SOURCE)
    g.bind("mlclasse", MLCLASSE)
    g.bind("srctype", SRCTYPE)
    g.bind("rico", RICO)
    g.bind("time", TIME)
    
    registres = []
    digit_registers = []
    ets_record_ls = []
    cadastre_ls = []
    
    for rdf_entity in rdf_entities:
        #URI Cadastre (RecordSet and Instantiation)
        uri_cadastre_recordset = URIRef(SOURCE + 'CADASTRE_' + str(rdf_entity["archives"]) + '_' + rdf_entity["commune_folder"] + '_' + str(rdf_entity["date_infos"]))
        uri_inst_cadastre = URIRef(SOURCE + 'CADASTRE_' + str(rdf_entity["archives"]) + '_' + rdf_entity["commune_folder"] + '_' + str(rdf_entity["date_infos"]) + '_corpus')
        
         # URI ETS RecordSet
        uri_ets_recordset = URIRef(SOURCE +  rdf_entity["archives"] + '_' + rdf_entity["commune_folder"] + '_' + rdf_entity["type_registre"] + '_' + str(rdf_entity["date_infos"]))
        
        #Instantiation numérique de la page
        mlclasse = arkindex_class_to_skosconcept(rdf_entity["ml_classe"])
        
        uri_inst = URIRef(SOURCE + rdf_entity["uuid"] + '_' + rdf_entity["page_numeric_cote"])
        g.add((uri_inst, RDF.type, RICO.Instantiation))
        g.add((uri_inst, CAD.isSourceType, SRCTYPE.PageDeRegistre))
        uri_bnode_class = URIRef(BNode().n3())
        g.add((uri_inst, CAD.hasClasse, uri_bnode_class))
        g.add((uri_bnode_class, RDF.type, CAD.MLClasse))
        g.add((uri_bnode_class, CAD.hasClasseValue, URIRef(MLCLASSE + mlclasse)))
        g.add((uri_inst, RICO.identifier, Literal(rdf_entity["page_numeric_cote"])))
        g.add((uri_inst, RICO.isOrWasDigitalInstantiationOf, URIRef(SOURCE + rdf_entity["page_numeric_cote"] + '_page')))
        g.add((uri_inst, RICO.isOrWasComponentOf, URIRef(SOURCE + rdf_entity["num_folder"])))
        g.add((uri_inst, CAD.URL,Literal(rdf_entity["iiif_url"])))
        
        #Record de la page
        uri_record = URIRef(SOURCE + rdf_entity["page_numeric_cote"] + '_page')
        g.add((uri_record, RDF.type, RICO.Record))
        g.add((uri_inst, CAD.isSourceType, SRCTYPE.PageDeRegistre))
        g.add((uri_record, RICO.isOrWasIncludedIn, uri_ets_recordset)) #Set de registres d'un type donné

        if rdf_entity["paper_cote"] not in registres:
            registres.append([rdf_entity["paper_cote"],rdf_entity["num_folder"]])


    for registre in registres:
        #Instantiation physique
        uri_registre_inst_phys = URIRef(SOURCE + rdf_entity["archives"] + '_' + registre[0])
        g.add((uri_registre_inst_phys, RDF.type, RICO.Instantiation))
        g.add((uri_registre_inst_phys, CAD.isSourceType, SRCTYPE.EtatsDeSections))
        g.add((uri_registre_inst_phys, RICO.identifier, Literal(registre[0])))
        g.add((uri_registre_inst_phys, RICO.hasOrHadPhysicalLocation, Literal("Archives Départementales du Val-de-Marne (94)")))
        g.add((uri_registre_inst_phys, RICO.isOrWasInstantiationOf, uri_ets_recordset))
        g.add((uri_registre_inst_phys, RICO.isOrWasComponentOf, uri_inst_cadastre))
        #Instantiation numérique
        uri_registre_inst_num = URIRef(SOURCE + registre[1])
        g.add((uri_registre_inst_num, RDF.type, RICO.Instantiation))
        g.add((uri_registre_inst_num, CAD.isSourceType, SRCTYPE.EtatsDeSections))
        g.add((uri_registre_inst_num, RICO.isOrWasComponentOf, uri_inst_cadastre))
        g.add((uri_registre_inst_phys, RICO.hasOrHadDerivedInstantiation, uri_registre_inst_num))
        g.add((uri_registre_inst_phys, RICO.hasOrHadDerivedInstantiation, uri_registre_inst_num))
        
        #Lien Instantiation numérique
        if registre[1] not in digit_registers:
            digit_registers.append(registre[1])
            g.add((uri_registre_inst_num, RDF.type, RICO.Instantiation))
            g.add((uri_registre_inst_num, RICO.identifier, Literal(registre[1]))) ;
            g.add((uri_registre_inst_num, RICO.isOrWasDigitalInstantiationOf, uri_ets_recordset))

    #Cadastre Record set
    if uri_ets_recordset not in ets_record_ls:
        #ETS Record Set (concept)
        ets_record_ls.append(uri_ets_recordset)
        g.add((uri_ets_recordset, RDF.type, RICO.RecordSet))
        g.add((uri_ets_recordset, CAD.isSourceType, URIRef(SRCTYPE + ets_type(rdf_entity["type_registre"]))))
        g.add((uri_ets_recordset, RICO.identifier, Literal(rdf_entity["type_registre"], datatype=XSD.string)))
        g.add((uri_ets_recordset, RICO.location, Literal(rdf_entity["commune"], datatype=XSD.string)))
        g.add((uri_ets_recordset, RICO.name, Literal(f"Etats de sections de {rdf_entity['commune']} ({rdf_entity['date_infos']})", datatype=XSD.string)))
        g.add((uri_ets_recordset, RICO.isOrWasIncludedIn, uri_cadastre_recordset))
        uri_doc_date = URIRef(BNode().n3())
        g.add((uri_ets_recordset, RICO.hasCreationDate, uri_doc_date))
        g.add((uri_doc_date, RDF.type, ADDR.CrispTimeInstant))
        g.add((uri_doc_date, ADDR.timeCalendar, TIME.Gregorian))
        g.add((uri_doc_date, ADDR.timePrecision, TIME.Year))
        g.add((uri_doc_date, ADDR.timeStamp, Literal(rdf_entity["date_registre"], datatype=XSD.dateTimeStamp)))
        uri_info_date = URIRef(BNode().n3())
        g.add((uri_ets_recordset, ADDR.hasTime, uri_info_date))
        g.add((uri_info_date, RDF.type, ADDR.CrispTimeInstant))
        g.add((uri_info_date, ADDR.timeCalendar, TIME.Gregorian))
        g.add((uri_info_date, ADDR.timePrecision, TIME.Year))
        g.add((uri_info_date, ADDR.timeStamp, Literal(rdf_entity["date_infos"], datatype=XSD.dateTimeStamp)))
        

    #Cadastre RecordSet and Instantiations
    if uri_cadastre_recordset not in cadastre_ls:
        g.add((uri_cadastre_recordset, RDF.type, RICO.RecordSet))
        g.add((uri_cadastre_recordset, CAD.isSourceType, SRCTYPE.Cadastre))
        g.add((uri_inst_cadastre, RDF.type, RICO.Instantiation))
        g.add((uri_inst_cadastre, CAD.isSourceType, SRCTYPE.Cadastre))
        g.add((uri_inst_cadastre, RICO.isOrWasInstantiation, uri_cadastre_recordset))
        
    return g

def generate_rdf_resource_event(g, page):
    """
    Create rdf resources of type LANDMARK and of type RECORD using an annotated page table json
    """
    ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
    CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
    EVENT = Namespace("http://rdf.geohistoricaldata.org/id/event/")
    CAD_ETYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/eventType/")
    TIME = Namespace("http://www.w3.org/2006/time#")
        
    g.bind("addr", ADDR)
    g.bind("cad", CAD)
    g.bind("cad_etype", CAD_ETYPE)
    g.bind("time", TIME)
    g.bind("event", EVENT)
    
    uri_event = URIRef(EVENT + "CADASTRE_LHAY_" + str(page["context"]["date"]))
    g.add((uri_event, RDF.type, ADDR.Event))
    g.add((uri_event, CAD.isEventType, CAD_ETYPE.CadastreCreation))
    uri_event_time = URIRef(BNode().n3())
    g.add((uri_event, ADDR.hasTime, uri_event_time))
    g.add((uri_event_time, RDF.type, ADDR.CrispTimeInstant))
    g.add((uri_event_time, ADDR.timeCalendar, TIME.Gregorian))
    g.add((uri_event_time, ADDR.timePrecision, TIME.Year))
    g.add((uri_event_time, ADDR.timeStamp, Literal(page["context"]["date"], datatype=XSD.dateTimeStamp)))

def generate_rdf_resource_plot_landmark(g, page, page_uuid):
    """
    Create rdf resources of type LANDMARK and of type RECORD using an annotated page table json
    """
    ADDR = Namespace("http://rdf.geohistoricaldata.org/def/address#")
    CAD = Namespace("http://rdf.geohistoricaldata.org/def/cadastre#")
    CAD_ATYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/")
    CAD_LTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/")
    CHANGE = Namespace("http://rdf.geohistoricaldata.org/id/change/")
    CTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/changeType/")
    EVENT = Namespace("http://rdf.geohistoricaldata.org/id/event/")
    CAD_ETYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/eventType/")
    LANDMARK = Namespace("http://rdf.geohistoricaldata.org/id/landmark/")
    LR = Namespace("http://rdf.geohistoricaldata.org/id/landmarkRelation/")
    LRTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/address/landmarkRelationType/")
    MLCLASSE =  Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/mlClasse/")
    PNATURE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/plotNature/")
    SOURCE = Namespace("http://rdf.geohistoricaldata.org/id/source/")
    SRCTYPE = Namespace("http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/")
    RICO = Namespace("https://www.ica.org/standards/RiC/ontology#")
    TAXPAYER = Namespace("http://rdf.geohistoricaldata.org/id/taxpayer/")
    TIME = Namespace("http://www.w3.org/2006/time#")
        
    g.bind("addr", ADDR)
    g.bind("cad", CAD)
    g.bind("cad_atype", CAD_ATYPE)
    g.bind("cad_ltype", CAD_LTYPE)
    g.bind("change", CHANGE)
    g.bind("ctype", CTYPE)
    g.bind("event", EVENT)
    g.bind("landmark", LANDMARK)
    g.bind("landmarkRelation", LR)
    g.bind("lrtype", LRTYPE)
    g.bind("mlclasse", MLCLASSE)
    g.bind("pnature", PNATURE)
    g.bind("source", SOURCE)
    g.bind("srctype", SRCTYPE)
    g.bind("rico", RICO)
    g.bind("taxpayer", TAXPAYER)
    g.bind("time", TIME)

    uri_event = URIRef(EVENT + "CADASTRE_LHAY_" + str(page["context"]["date"]))
    
    counter = 0
    for line in page["entities"]:
        # Line RecordPart
        uri_line = URIRef(SOURCE + line["uri"] + "_line")
        g.add((uri_line, RDF.type, RICO.Instantiation))
        g.add((uri_line, CAD.isSourceType, SRCTYPE.LigneEtatDeSection))
        g.add((uri_line, DCTERMS.identifier, Literal(str(counter), datatype=XSD.string)))
        g.add((uri_line, RICO.isOrWasComponent, URIRef(SOURCE + page_uuid + '_' + page["context"]["page_numeric_cote"])))
        g.add((uri_line, CAD.coordinatesInImageSystem, Literal(page["objects"][counter]["polygon"], datatype=XSD.string)))
        g.add((uri_line, CAD.transcription, Literal(page["objects"][counter]["text"], datatype=XSD.string)))
        
        #Plot
        uri_plot_landmark = URIRef(LANDMARK + line["uri"] + "_plot")
        g.add((uri_plot_landmark, RDF.type, ADDR.Landmark))
        g.add((uri_plot_landmark, ADDR.isLandmarkType, CAD_LTYPE.Plot))
        g.add((uri_plot_landmark, RDFS.label, Literal(line["Ⓕ"]['plot_id'] + " (" + page["context"]["commune"] + ")", datatype = XSD.string)))
        g.add((uri_plot_landmark, SKOS.prefLabel, Literal(line["Ⓕ"]['plot_id'] + " (" + page["context"]["commune"] + ")", datatype = XSD.string)))
        g.add((uri_plot_landmark, DCTERMS.identifier, Literal(line["Ⓕ"]['plot_id'], datatype=XSD.string)))
        g.add((uri_plot_landmark, CAD.sourcedFrom, uri_line))

        #Change Appearance
        #uri_change_landmark = URIRef(BNode().n3())
        uri_change_landmark = URIRef(CHANGE + line["uri"] + "_plot_change")
        g.add((uri_change_landmark, RDF.type, ADDR.Change))
        g.add((uri_change_landmark, ADDR.appliedTo, uri_plot_landmark))
        g.add((uri_change_landmark, ADDR.dependsOn, uri_event))
        g.add((uri_change_landmark, ADDR.isChangeType, URIRef(CTYPE.LandmarkAppearance)))
        
        #Attributes
        cell_types = list(line.keys())
        if 'Ⓔ' in cell_types: #NATURE
            uri_att_nat = URIRef(BNode().n3())
            g.add((uri_plot_landmark, ADDR.hasAttribute, uri_att_nat))
            g.add((uri_att_nat, RDF.type, ADDR.Attribute))
            g.add((uri_att_nat, ADDR.isAttributeType, CAD_ATYPE.PlotNature))
            for uri in line["Ⓔ"]["uris"] :
                uri_att_nat_v = URIRef(BNode().n3())
                g.add((uri_att_nat, ADDR.hasAttributeVersion, uri_att_nat_v))
                g.add((uri_att_nat_v, RDF.type, ADDR.AttributeVersion))
                if uri != "NIL":
                    g.add((uri_att_nat_v, CAD.hasPlotNature, URIRef(uri)))
                elif uri == "NIL" and len(line["Ⓔ"]["interpreted_text"]) > 0:
                    g.add((uri_att_nat_v, CAD.hasPlotNature, Literal(line["Ⓔ"]["interpreted_text"],datatype=XSD.string)))
                uri_change_att = URIRef(CHANGE + line["uri"] + "_'Ⓔ'_change")
                #uri_change_att = URIRef(CHANGE + str(uuid.uuid()))
                g.add((uri_change_att, RDF.type, ADDR.Change))
                g.add((uri_change_att, ADDR.appliedTo, uri_att_nat))
                g.add((uri_change_att, ADDR.makesEffective, uri_att_nat_v))
                g.add((uri_change_att, ADDR.dependsOn, uri_event))
                g.add((uri_change_att, ADDR.isChangeType, URIRef(CTYPE.AttributeVersionAppearance)))

        if 'Ⓒ' in cell_types and "uris" in list(line["Ⓒ"].keys()): #TAXPAYER
            uris = [uri for uri in line["Ⓒ"]["uris"] if line["Ⓒ"]["interpreted_text"].lower() != "missing" or len(uri) > 0]
            if len(uris) > 0:
                uri_att = URIRef(BNode().n3())
                g.add((uri_plot_landmark, ADDR.hasAttribute, uri_att))
                g.add((uri_att, RDF.type, ADDR.Attribute))
                g.add((uri_att, ADDR.isAttributeType, CAD_ATYPE.PlotTaxpayer))
                for uri in uris:
                    uri_att_v = URIRef(BNode().n3())
                    g.add((uri_att, ADDR.hasAttributeVersion, uri_att_v))
                    g.add((uri_att_v, RDF.type, ADDR.AttributeVersion))
                    g.add((uri_att_v, CAD.hasPlotTaxpayer, URIRef(uri)))
    
                    uri_change_att = URIRef(CHANGE + line["uri"] + "_'Ⓒ'_change")
                    #uri_change_att = URIRef(CHANGE + str(uuid.uuid()))
                    g.add((uri_change_att, RDF.type, ADDR.Change))
                    g.add((uri_change_att, ADDR.appliedTo, uri_att))
                    g.add((uri_change_att, ADDR.makesEffective, uri_att_v))
                    g.add((uri_change_att, ADDR.dependsOn, uri_event))
                    g.add((uri_change_att, ADDR.isChangeType, URIRef(CTYPE.AttributeVersionAppearance)))
                    g.add((URIRef(uri), CAD.sourcedFrom, uri_line))
        else:
            print(str(uri_line), "EMPTY")

        if 'Ⓓ' in cell_types and "uris" in list(line["Ⓓ"].keys()) and line["Ⓓ"]["interpreted_text"].lower() not in ("missing",""): #PLOTADDRESS Landmark Relation
            #uri_landmark_relation = URIRef(uuid.uuid())
            
            p1 = str(uri_plot_landmark).replace("http://rdf.geohistoricaldata.org/id/landmark/","")
            p2 = line["Ⓓ"]["uris"].replace("http://rdf.geohistoricaldata.org/id/landmark/","")
            uri_landmark_relation = URIRef(LR + p1 + '_' + p2)
            g.add((uri_landmark_relation, RDF.type, ADDR.LandmarkRelation))
            g.add((uri_landmark_relation, ADDR.isLandmarkRelationType, LRTYPE.Undefined)) ;
            g.add((uri_landmark_relation, ADDR.locatum, uri_plot_landmark)) ;
            g.add((uri_landmark_relation, ADDR.relatum, URIRef(line["Ⓓ"]["uris"]))) ;

            uri_att = URIRef(BNode().n3())
            g.add((uri_plot_landmark, ADDR.hasAttribute, uri_att))
            g.add((uri_att, RDF.type, ADDR.Attribute))
            g.add((uri_att, ADDR.isAttributeType, CAD_ATYPE.PlotAddress))
            uri_att_v = URIRef(BNode().n3())
            g.add((uri_att, ADDR.hasAttributeVersion, uri_att_v))
            g.add((uri_att_v, RDF.type, ADDR.AttributeVersion))
            g.add((uri_att_v, CAD.hasPlotAddress, URIRef(uri_landmark_relation)))

            #uri_change_att = URIRef(CHANGE + str(uuid.uuid()))
            uri_change_att = URIRef(CHANGE + line["uri"] + "_'Ⓓ'_change")
            g.add((uri_change_att, RDF.type, ADDR.Change))
            g.add((uri_change_att, ADDR.appliedTo, uri_att))
            g.add((uri_change_att, ADDR.makesEffective, uri_att_v))
            g.add((uri_change_att, ADDR.dependsOn, uri_event))
            g.add((uri_change_att, ADDR.isChangeType, URIRef(CTYPE.AttributeVersionAppearance)))

            #Source of the landmark 
            g.add((URIRef(line["Ⓓ"]["uris"]), CAD.sourcedFrom, uri_line))

        #SECTION Landmark Relation
        #uri_landmark_relation = URIRef(BNode().n3())
        p1 = str(uri_plot_landmark).replace("http://rdf.geohistoricaldata.org/id/landmark/","")
        p2 = page["context"]["section"].replace("http://rdf.geohistoricaldata.org/id/landmark/","")
        uri_landmark_relation = URIRef(LR + p1 + '_' + p2)
        g.add((uri_landmark_relation, RDF.type, ADDR.LandmarkRelation))
        g.add((uri_landmark_relation, ADDR.isLandmarkRelationType, LRTYPE.Within)) ;
        g.add((uri_landmark_relation, ADDR.locatum, uri_plot_landmark)) ;
        g.add((uri_landmark_relation, ADDR.relatum, URIRef(page["context"]["section"]))) ;
        counter += 1