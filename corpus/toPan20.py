"""
Converts the Gutenberg corpus to the new PAN20 format.
"A"/"B" is appended to the IDs from the training / test set to make them
unique.

First unzip file with `unzip corpus.zip`.
There should be two subdirectories in this directory:
gutenberg_train, gutenberg_test
Then run `python toPan20.py`

Goal:
A .jsonl training / test file with each line:
{
    id: string,
    pair: [string, string]
    meta: {
        known_gbid: string
        known_author: string
        known_title: string
        unknown_gbid: string
        unknown_author: string
        unknown_title: string
    }
}

A .jsonl training / test TRUTH file with each line:
{
    id: string,
    same: boolean
}
Maybe added later for author IDs: authors: [string, string]
"""
import os
import csv
import json

def read_data(folder_name, suffix):
    data = []

    # Get meta
    with open(os.path.join(folder_name, 'meta.csv'), newline='') as f:
        meta = [x for x in csv.DictReader(f)]

    train_dir = [d for d in os.scandir(folder_name)]
    for dir_entry in train_dir:
        if dir_entry.name in ['meta.csv', 'truth.txt']:
            continue
        # Add ID and text pair
        with open(os.path.join(dir_entry.path, 'known01.txt'), 'r') as f:
            k = f.read()
        with open(os.path.join(dir_entry.path, 'unknown.txt'), 'r') as f:
            u = f.read()
        d = dict()
        d['id'] = f'{dir_entry.name}{suffix}'
        d['pair'] = [k, u]

        # Add meta
        m = [x for x in meta if dir_entry.name == x['case']][0].copy()
        m.pop('case')
        d['meta'] = m

        data.append(d)
    return sorted(data, key=lambda x: x['id'])


def read_truth(folder_name, suffix):
    truth = []
    with open(os.path.join(folder_name, 'truth.txt')) as f:
        for line in f:
            d = dict()
            pair_id, same = line.strip().split(' ')
            d['id'] = f'{pair_id}{suffix}'
            d['same'] = True if same == 'Y' else False
            truth.append(d)
    return truth


def persist_jsonl(file_name, obj):
    with open(os.path.join('pan20', file_name), 'w') as f:
        for o in obj:
            json.dump(o, f)
            f.write('\n')


def main():
    train = read_data('gutenberg_train', 'A')
    train_truth = read_truth('gutenberg_train', 'A')

    test = read_data('gutenberg_test', 'B')
    test_truth = read_truth('gutenberg_test', 'B')

    combined = train + test
    combined_truth = train_truth + test_truth

    os.makedirs('pan20', exist_ok=True)
    persist_jsonl('train-gb.jsonl', train)
    persist_jsonl('train-gb-truth.jsonl', train_truth)
    persist_jsonl('test-gb.jsonl', test)
    persist_jsonl('test-gb-truth.jsonl', test_truth)
    persist_jsonl('gb.jsonl', combined)
    persist_jsonl('gb-truth.jsonl', combined_truth)


if __name__ == '__main__':
    main()
