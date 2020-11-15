from pykeen.pipeline import pipeline
from pykeen.triples.triples_factory import TriplesFactory
from pykeen.triples.triples_factory import EntityMapping, RelationMapping
import pandas as pd
import numpy as np

import re

INVERSE_SUFFIX = '_inverse'

dataset = 'PharmKG'
train_path = f'../../data/{dataset}/train.tsv'
valid_path = f'../../data/{dataset}/valid.tsv'
test_path = f'../../data/{dataset}/test.tsv'

if dataset == 'PharmKG':
    _num_entities = 7601
    _num_relations = 28
elif dataset == 'hetionet':
    _num_entities = 19881
    _num_relations = 12
elif dataset == 'covid19':
    _num_entities = 15482
    _num_relations = 46
else:
    assert 0

def create_entity_mapping(triples) -> EntityMapping:
    """Create mapping from entity labels to IDs.

    :param triples: shape: (n, 3), dtype: str
    """
    # Split triples
    heads, tails = triples[:, 0], triples[:, 2]
    # Sorting ensures consistent results when the triples are permuted
    entity_labels = sorted(set(heads).union(tails))
    # Create mapping
    return {
        str(label): i
        for (i, label) in enumerate(entity_labels)
    }

def create_relation_mapping(relations: set) -> RelationMapping:
    """Create mapping from relation labels to IDs.

    :param relations: set
    """
    # Sorting ensures consistent results when the triples are permuted
    relation_labels = sorted(
        set(relations),
        key=lambda x: (re.sub(f'{INVERSE_SUFFIX}$', '', x), x.endswith(f'{INVERSE_SUFFIX}')),
    )
    # Create mapping
    return {
        str(label): i
        for (i, label) in enumerate(relation_labels)
    }

def get_triples_and_relations():
    names = ['head', 'relation', 'tail']
    train = pd.read_csv(train_path, sep='\t', header=None, names=names)
    valid = pd.read_csv(valid_path, sep='\t', header=None, names=names)
    test = pd.read_csv(test_path, sep='\t', header=None, names=names)
    
    df = train.append(valid).append(test).reset_index(drop=True)
    return df.values, set(df['relation'])

triples, relations = get_triples_and_relations()

entity_to_id = create_entity_mapping(triples)
relation_to_id = create_relation_mapping(relations)


train = TriplesFactory(path=train_path, entity_to_id=entity_to_id, relation_to_id=relation_to_id)
train._num_entities = _num_entities
train._num_relations = _num_relations
valid = TriplesFactory(path=valid_path, entity_to_id=entity_to_id, relation_to_id=relation_to_id)
valid._num_entities = _num_entities
valid._num_relations = _num_relations
test = TriplesFactory(path=test_path, entity_to_id=entity_to_id, relation_to_id=relation_to_id)
test._num_entities = _num_entities
test._num_relations = _num_relations

model = 'TransE'
result = pipeline(
    model=model,
    training_triples_factory=train,
    validation_triples_factory=valid,
    testing_triples_factory=test,
    training_kwargs={'num_epochs':300}, # 30
    model_kwargs={'embedding_dim':300},
    stopper='early',
    stopper_kwargs={'frequency':10, 'stopped':True, 'patience':1},
    evaluation_kwargs={'batch_size':32},
    optimizer_kwargs={'lr':0.1},
)



# =============================================================================
# print(result.metric_results.hits_at_k['avg'])
# print(result.metric_results.hits_at_k['pred'])
# np.save(f'{dataset}_{model}_pred.npy', result.metric_results.hits_at_k['pred'])
# =============================================================================
print(result)
result.save_to_directory(f'{dataset}_{model}')
