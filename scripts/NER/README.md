# Named Entities Recognition

## Requirements

## Pipeline Overview  

* **`00_init-ner-gt`** – Use a few examples to generate additional annotated data with an LLM. Manual post-processing is required. The outputs are Brat Standoff annotations for Named Entity Recognition (NER).  
* **`01_prepare_dataset`** – Convert the manually corrected Brat Standoff annotations into a dataset compatible with the Hugging Face format.  
* **`02_fine_tuning`** – Fine-tune a NER model using the dataset created in `01_prepare_dataset`.  
* **`03_demo`** – Jupyter Notebook demonstrating the fine-tuned NER model in action.  
* **`04_inference_full_dataset`** – Use the fine-tuned model to annotate the entire dataset.

## TO DO
* Post-correction des annotations (Brat Standoff)
* Une fois les propriétaires désambiguisés, ne garder qu'une mention pour chacun (sauf si plusieurs intitulés très différents, à mettre dans le même subset)
* Ajouter les propriétaires du dataset "Gentilly"