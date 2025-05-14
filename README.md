# An end-to-end pipeline for knowledge graph population from 19th-century land registry digitised tables

## Abstract
Historical tables, such as administrative registers, represent vast and valuable sources of information for researchers. However, despite large-scale digitization efforts, extracting and structuring their content remains challenging. The French 19th-century Land Registry is a notable example: rich in detailed land use information, yet highly heterogeneous, and still largely underexploited. Although recent deep learning methods have improved information extraction (IE) from digitised documents, they often lack semantic structuring. Conversely, Semantic Table Interpretation (STI) techniques, mostly applied to natively digital tables, offer structuring and linking capabilities but are rarely used on historical sources. In this work, we propose a pipeline that combines deep learning-based IE with STI, guided by a domain ontology. The approach produces a knowledge graph that enables querying and exploration of historical records. We evaluate the resulting knowledge graph using several metrics, demonstrating the potential of our method for semantic enrichment of historical data.

## Requirements
* Python >= 3.10
    * Each *scripts/XX* subfolder requires a dedicated virtual environnement
* Computing resources
    * 2 GPUs with at least 45Go RAM required to train DAN
    * 1 GPU for YOLOv11 and Camembert-NER model fine-tuning
* A RDF triplestore :
    * We use Graph DB for these experiments 

## Repository structure
```
├── gold-standard
├── scripts
|   ├── CLASSIF            <- Train YOLOv11 classifier for page classification
│   ├── DAN                <- Train DAN for information extraction from historical tables
│   ├── NER                <- Train a named entity recognition model to structure taxpayers mentions
│   ├── EL                 <- Entity linking and entity creation approaches
│   ├── EVAL               <- Final graph evaluation
│   ├── utils              <- Useful tools and scripts
│
├── LICENCE.md
├── README.md
└── appendix.pdf              <- Submitted paper with appendix (includes extended evaluation)
```

## Datasets
These datasets have been produced using pages from the initial registers (*états de sections* in french) of the 19th-century french land registry using images from the Val-de-Marne archives.
* **Page classification** : [Download on Zenodo, https://doi.org/10.5281/zenodo.15386606](https://zenodo.org/10.5281/zenodo.15386606)
* **Information extraction** : [Download on Zenodo, https://doi.org/10.5281/zenodo.15411507](https://zenodo.org/10.5281/zenodo.15411507)
* **Gold-standard KG** : TO ADD

## Models
Here are the path to the fine-tuned models for page classification, information extraction and named-entity recognition.
* **YOLOv11-19lr-ir-94** : TO ADD
* **DAN-19lr-ir-94** : TO ADD

*NB : 19lr (19th century land registry), ir (initial registers), 94 (Val-de-Marne departement archives)*

## Acknowledgement

This work is supported by the French National Mapping Agency (IGN) and the French Ministery of Defense - Innovation Defense Lab (AID).

Images have been provided by the Archives of the French Departement of Val-de-Marne (94).