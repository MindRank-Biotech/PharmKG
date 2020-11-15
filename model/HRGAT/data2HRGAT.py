import pandas as pd

path = '../../data/PharmKG'
train = pd.read_csv(f'{path}/train.tsv', header=None, sep='\t', names=['h', 'r', 't'])
valid = pd.read_csv(f'{path}/valid.tsv', header=None, sep='\t', names=['h', 'r', 't'])
test = pd.read_csv(f'{path}/test.tsv', header=None, sep='\t', names=['h', 'r', 't'])

entity = set(train['h']).union(train['t'])
entity = entity.union(valid['h']).union(valid['t'])
entity = entity.union(test['h']).union(test['t'])

entity = pd.DataFrame({'name':list(entity)})
entity['idx'] = entity.index
entity.to_csv(f'{path}/entity2id.txt', header=None, sep='\t', index=False)

relation = set(train['r'])
relation = pd.DataFrame({'name':list(relation)})
relation['idx'] = relation.index
relation.to_csv(f'{path}/relation2id.txt', header=None, sep='\t', index=False)


train.to_csv(f'{path}/train.txt', header=None, sep='\t', index=False)
valid.to_csv(f'{path}/valid.txt', header=None, sep='\t', index=False)
test.to_csv(f'{path}/test.txt', header=None, sep='\t', index=False)