# Information extraction in historical tables with DAN

## Documentation
* [DAN (Teklia)](https://gitlab.teklia.com/atr/dan)
* [DAN Documentation ](https://atr.pages.teklia.com/dan/)
* [Nerval (Teklia)](https://gitlab.teklia.com/ner/nerval)

## Requirements
* Python >= 3.10
* [OPTIONAL] Acces to an Arkindex instance or an SQLite database exported from Arkindex

## Installation
1. Create a virtual environnement
- ```python3 -m venv .venv/venv_dan```

2. Activate the environnement : 
    * ```source .venv_dan/bin/activate```
    * ```.venv/venv_dan/bin/activate```

3. Execute ```setup.sh``` to install atr-DAN and Nerval:
            * ```chmod +x setup.sh```
            * ```./setup.sh```

## Notebooks
* ```00-create_train_val_test.ipynb``` : create train/val/test subsets using records metadata
* ```10-prepare-data-dan.ipynb``` : convert the SQLITE database to the DAN training dataset
* ```20-train-dan.ipynb``` : fine-tune DAN model
* ```21-display-training-metrics.ipyn``` : create graphs representing the evolution of the loss value and metrics (CER etc.) during the training
* ```22-fix-parallel-training-troubles.ipynb``` : used to fix a bug in the model if training was performed on several GPUs, required to infer on new data
* ```30-evaluation-dan.ipynb``` : evaluation of DAN ouputs on val/test
* ```31-visualisation.ipynb``` : tool to visualise automatically produced annotations
* ```40-evaluation-dan.ipynb``` : inference on new pages

## Help
* To track metrics evolution during training :
    * Launch tensorboard ```tensorboard --logdir . --host localhost``` in the folder where the results are saved (ex: ```outputs/train_110324/results/```)

### Important : To fix before running DAN
* The special character **§** is used in the training dataset. BUT, it is also used in the Nerval library code as a separator. In the Nerval library installation, in you virtual environnement, please replace the § by another special character (like £) to avoid any error (*nerval/parse.py* file).
* If you want to train DAN using prralelized processus (e.g. use_ddp = True in the config file) :
    * In the file  ```dan/ocr/manager/training.py``` of the atr-dan library in your virtual environnement, in the function *validate*, please comment this code extract:
```
self.writer.add_image(
                        f"valid_images/{batch_data['names'][0]}",
                        result_tensor,
                        self.latest_epoch,
                    )

 ```