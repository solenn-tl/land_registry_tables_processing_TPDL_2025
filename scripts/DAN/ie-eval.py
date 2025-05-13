import subprocess

ROOT = "/home/STual/DAN-cadastre"
GT_JSON = ROOT + "/dataset2/page_dataset/split.json"
GT_IOB_FOLDER = ROOT + "/scripts/DAN/iob/labels"
PRED_DAN_FOLDER = "/home/STual/DAN-cadastre/inference/training120325_config2025_prod_2000epochs"
PRED_IOB_FOLDER = "/home/STual/DAN-cadastre/inference/iob/predictions"
DAN_TOKENS = "/home/STual/DAN-cadastre/dataset2/tokens.yml"

# Execute IE EVAL
ie_command = f"ie-eval all --label-dir {GT_IOB_FOLDER + '/test'} --prediction-dir {PRED_IOB_FOLDER + '/test'} --by-category"
result_ie = subprocess.run(ie_command, capture_output=True, text=True)
