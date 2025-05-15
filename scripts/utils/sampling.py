from sklearn.model_selection import StratifiedGroupKFold

def stratified_groups(df, groupby_column, n_split=5, suffle=True, random_state=42):
    # Use scikit-learn to split the dataset into a training set and a testing set
    # We need stratification according to the column "classe"
    
    skgf = StratifiedGroupKFold(n_splits=n_split, shuffle=suffle, random_state=random_state)  # split == 5 ⇔ 80% train, 20% test
    for split_id, (train_index_, test_index) in enumerate(skgf.split(df, df['stratification_id'], groups=df[groupby_column])):
        if split_id > 0:
            break
        print("")
        print(f"Split {split_id}")
        train_ = df.iloc[train_index_]
        train_index, val_index = next(skgf.split(train_, train_['stratification_id'], groups=train_[groupby_column]))
        train = train_.iloc[train_index]
        val = train_.iloc[val_index]
        test = df.iloc[test_index]
        
        print(f"Train size: {len(train)}")
        print(f"Val size: {len(val)}")
        print(f"Test size: {len(test)}")
        print("")
        print(f"Train Stratification id: {train['stratification_id'].value_counts()}")
        print(f"Val Stratification id: {val['stratification_id'].value_counts()}")
        print(f"Test Stratification id: {test['stratification_id'].value_counts()}")
        print("")
        print(f"Train {groupby_column}: {train['commune'].value_counts()}")
        print(f"Val {groupby_column}: {val['commune'].value_counts()}")
        print(f"Test {groupby_column}: {test['commune'].value_counts()}")
        print("")
    return train, val, test