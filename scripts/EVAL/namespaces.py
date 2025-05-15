prefixes = """
PREFIX cad: <http://rdf.geohistoricaldata.org/def/cadastre#>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xml: <http://www.w3.org/XML/1998/namespace/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX voaf: <http://purl.org/vocommons/voaf#>
PREFIX cc: <http://creativecommons.org/ns#>
PREFIX vann: <http://purl.org/vocab/vann/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX organization: <http://www.w3.org/ns/org#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX pwikidata: <https://www.wikidata.org/wiki/Property:>
PREFIX igeo: <http://rdf.insee.fr/def/geo#>
PREFIX atype: <http://rdf.geohistoricaldata.org/id/codes/address/attributeType/>
PREFIX ctype: <http://rdf.geohistoricaldata.org/id/codes/address/changeType/>
PREFIX ltype: <http://rdf.geohistoricaldata.org/id/codes/address/landmarkType/>
PREFIX lrtype: <http://rdf.geohistoricaldata.org/id/codes/address/landmarkRelationType/>
PREFIX cad_atype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/>
PREFIX cad_ltype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/>
PREFIX cad_etype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/eventType/>
PREFIX cad_ctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/changeType/>
PREFIX cad_spval: <http://rdf.geohistoricaldata.org/id/codes/cadastre/specialCellValue/>
PREFIX pnature: <http://rdf.geohistoricaldata.org/id/codes/cadastre/plotNature/>
PREFIX srctype: <http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/>
PREFIX mlclasse: <http://rdf.geohistoricaldata.org/id/codes/cadastre/mlClasse/>
PREFIX activity: <http://rdf.geohistoricaldata.org/id/codes/cadastre/activity/>
"""

prefixes_dict = {"http://rdf.geohistoricaldata.org/def/address#": "addr:",
"https://www.ica.org/standards/RiC/ontology#":"rico:",
"http://rdf.geohistoricaldata.org/def/cadastre#":"cad:",
"http://rdf.geohistoricaldata.org/id/landmark/":"landmark:",
"http://rdf.geohistoricaldata.org/id/source/":"source:",
"http://rdf.geohistoricaldata.org/id/taxpayer/":"taxpayer:",
"http://rdf.geohistoricaldata.org/id/event/":"event:",
"http://rdf.geohistoricaldata.org/id/codes/address/attributeType/":"atype:",
"http://rdf.geohistoricaldata.org/id/codes/address/changeType/":"ctype:",
"http://rdf.geohistoricaldata.org/id/codes/address/landmarkType/":"ltype:",
"http://rdf.geohistoricaldata.org/id/codes/address/landmarkRelationType/":"lrtype:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/attributeType/":"cad_atype:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/landmarkType/":"cad_ltype:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/eventType/":"cad_etype:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/changeType/":"cad_ctype:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/specialCellValue/":"cad_spval:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/plotNature/":"pnature:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/sourceType/":"srctype:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/mlClasse/":"mlclasse:",
"http://rdf.geohistoricaldata.org/id/codes/cadastre/activity/":"activity:",
"http://www.w3.org/2006/time#":"time:",
"http://www.w3.org/2004/02/skos/core#":"skos:",
"http://www.w3.org/2001/XMLSchema#":"xsd:",
"http://www.w3.org/XML/1998/namespace/":"xml:",
"http://www.w3.org/2002/07/owl#":"owl:",
"http://www.w3.org/ns/prov#":"prov:",
"http://www.w3.org/ns/org#":"organization:",
"http://www.w3.org/2000/01/rdf-schema#":"rdfs:",
"http://www.w3.org/1999/02/22-rdf-syntax-ns#":"rdf:",
"http://purl.org/vocab/vann/":"vann:",
"http://purl.org/dc/terms/":"dcterms:",}
