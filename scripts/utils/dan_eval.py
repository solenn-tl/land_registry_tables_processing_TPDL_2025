import glob
import pandas as pd

def read_metric_yaml(yaml_file):
    with open(yaml_file,'r',encoding='utf8') as f:
        lines = f.readlines()
    values = []
    keys = []
    for l in lines:
        l = l.replace('\n','')
        key, value = l.split(': ')
        values.append(float(value))
        keys.append(key)
    assert len(values) == len(keys)
    return values, keys
    
def concat_metrics(folder):
    files = glob.glob(folder + "/predict_*.yaml")
    files = sorted(files)
    keys = read_metric_yaml(files[0])[1]
    keys.append("subset")
    test = read_metric_yaml(files[0])[0]
    test.append("test")
    train = read_metric_yaml(files[1])[0]
    train.append("train")
    val = read_metric_yaml(files[2])[0]
    val.append("val")
    frames = [train,val,test]
    df = pd.DataFrame(frames, columns = keys)
    df = df.set_index('subset')
    df = df.reindex(columns=['cer','cer_no_token','wer','wer_no_punct','wer_no_token','ner','nb_samples','nb_chars','nb_chars_no_token','nb_tokens','nb_words','nb_words_no_punct','nb_words_no_token','sample_time','time'])
    return df