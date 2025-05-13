# Information extraction in historical tables with DAN

## Documentation
* [DAN (Teklia)](https://gitlab.teklia.com/atr/dan)
* [DAN Documentation ](https://atr.pages.teklia.com/dan/)
* [Nerval (Teklia)](https://gitlab.teklia.com/ner/nerval)

## Requirements
* Python >= 3.10
* Arkindex instance with the annotations and training subsets. SQLite database exported from Arkindex can also be used if contains the training subsets.

## Installation
1. Create a virtual environnement
- ```cd DAN-cadastre```
- ```python3 -m venv .venv_dan```

2. Activate the environnement : 
    * ```source .venv_dan/bin/activate```
    * ```.venv_dan/bin/activate```

3. Each subpart of the pipeline has its requirement file (see ```scripts/XX```)
        * Execute ```setup.sh``` pour installer Nerval et DAN :
            * ```chmod +x setup.sh```
            * ```./setup.sh```

## Notebooks
### 1. Create train/val/test subsets
* ```00-create_train_val_test.ipynb```
### 2. Convert data from SQLITE database to DAN training dataset
* ```10-prepare-data-dan.ipynb```
### 3. Train DAN
* ```20-train-dan.ipynb```
### 4. DAN Evaluation 
* ```30-evaluation-dan.ipynb```
* ```31-fix-parallel-training-troubles.ipynb``` : *used to fix a bug in the model if training on several GPUs, required to infer on new data*
### 5. Inference on new images
* ```40-inference-dan.ipynb```

## Help
* Lancer tensorboard ```tensorboard --logdir . --host localhost``` dans le dossier où sont contenus les résultats du modèle (ex: ```outputs/train_110324/results/```)

## To fix before running DAN
* Le token spécial § est utilisé dans mes annotations mais est aussi utilisé dans NERVAL comme séparateur.
* 11/03/25 : Erreur quand on utilise l'entraînement avec parallélisation des processus (use_ddp = True)
   * Dans le fichier ```dan/ocr/manager/training.py``` fonction *validate*, commenter la portion de code suivante :
     ```
    self.writer.add_image(
                            f"valid_images/{batch_data['names'][0]}",
                            result_tensor,
                            self.latest_epoch,
                        )

     ```