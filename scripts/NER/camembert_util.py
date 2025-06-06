import numpy as np
import nltk
from xml.dom.minidom import parseString
from datasets import Dataset
import evaluate
from config import logger
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    EarlyStoppingCallback,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
)

#Label ID of original DAS code
LABELS_ID = {
    "O+O" : 0,
    "I-name+O" : 1,
    "I-firstnames+O" : 2,
    "I-activity+O" : 3,
    "I-address+O" : 4,
    "I-title+O" : 5,
    "I-familystatus+O" : 6,
    "I-birthname+O" : 7,
}
# Entry point
def init_model(model_name, training_config,labels_dict):
    """
    Init model function
    In :
     - model_name : name of the model load from transformers library
     - training_config : training params (eval steps, learnig rate etc)
     
     Out :
     - model : model loads from Transformers library without pre-training or fine-tuning ; with config and weights
     - tokenizer : 
     - training_args : 
    """
    logger.info(f"Model {model_name}")
    #Load the tokenizer associated with the pretrained model
    tokenizer = AutoTokenizer.from_pretrained(model_name,local_files_only=True)
    
    #output_path = save_model_path or "/tmp/bert-model"    
    training_args = TrainingArguments(**training_config) 
    #** en python : permet de transformer le dictionnaire clé-valeur défini à l'extérieur de la fonction en une liste d'arguments pour la fonction

    # Load the pretrained model
    model = AutoModelForTokenClassification.from_pretrained( 
        model_name,
        num_labels=len(LABELS_ID),
        ignore_mismatched_sizes=True,
        id2label={v: k for k, v in LABELS_ID.items()},
        label2id=LABELS_ID
    )
    return model, tokenizer, training_args

# Main loop : entrainement
def train_eval_loop(model, training_args, tokenizer, labels_dict, train, dev, test, patience=3):
    """
    In :
    - model
    - training_args
    - tokenizer
    - trainset
    - devset
    - testset
    - patience
    """
    data_collator = DataCollatorForTokenClassification(tokenizer) #Permet de créer les batch à partir du dataset
    #Trainer tool
    trainer = Trainer(
            model,
            training_args,
            train_dataset=train,
            eval_dataset=dev,
            data_collator=data_collator,#batchs
            tokenizer=tokenizer,#tokenizer
            compute_metrics=compute_metrics,
            callbacks=[ #callback : prend des décisions en fonction de l'avancement de l'entrainement
                EarlyStoppingCallback(early_stopping_patience=patience)
            ],
        )
    
    trainer.train() #Train
    return trainer.evaluate(test), trainer.evaluate() #Evaluation result on test and dev sets

# Metrics

def compute_metrics(p):
    
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2) #Max value
    label_list = list(LABELS_ID.keys())
    
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    metric = evaluate.load("seqeval")
    results = metric.compute(predictions=true_predictions, references=true_labels)
        
    return { #Sortie
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"]
    }
   
# =============================================================================
# region ~ Data conversion utils for Hugginface

_convert_tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")

def create_huggingface_dataset(entries):
    # Creates a Huggingface Dataset from a set of NER-XML entries
    tokenized_entries = [word_tokens_from_xml(entry) for entry in entries]
    word_tokens, labels = zip(*tokenized_entries)
    ds = Dataset.from_dict({"tokens": word_tokens, "ner_tags": labels})
    return ds.map(assign_labels_to_bert_tokens, batched=True)


def assign_labels_to_bert_tokens(examples):
    bert_tokens = _convert_tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )
    prev_word_id = None
    labels = []
    for id, label in enumerate(examples["ner_tags"]):
        labels_ids = []
        for word_id in bert_tokens.word_ids(batch_index=id):
            # Set the label only on the first token of each word
            if word_id in [None, prev_word_id]:
                labels_ids.append(-100)
            else:
                label_id = LABELS_ID[label[word_id]]
                labels_ids.append(label_id)
            prev_word_id = word_id

        labels.append(labels_ids)

    bert_tokens["labels"] = labels
    return bert_tokens


# convenient word tokenizer to create IOB-like data for the BERT models
nltk.download("punkt")

def word_tokens_from_xml(entry):
    """
    Create IOB one level labels
    """
    w_tokens = []
    labels = []

    entry_xml = f"<x>{entry}</x>"
    x = parseString(entry_xml).getElementsByTagName("x")[0]

    for el in x.childNodes:
        if el.nodeName == "#text":
            cat = "O"
            txt = el.nodeValue
        else:
            cat = f"I-{el.nodeName}"
            txt = el.childNodes[0].nodeValue

        words = nltk.word_tokenize(txt, language="fr", preserve_line=True)
        w_tokens += words
        labels += [cat] * len(words)

    return w_tokens, labels

# endregion
