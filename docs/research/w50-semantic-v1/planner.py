"""Small legacy planner. The benchmark requests changes in successive stages."""
import json


def merge_windows(windows, merge_touching=False):
    raise NotImplementedError('merge_windows is not implemented')


def build_plan(rows):
    return [{'inventory_tag':row['inventory_tag'],
             'label_exact':row['label_exact'].strip(),
             'sequence_exact':str(int(row['sequence_exact'])),
             'windows':merge_windows(row['windows'])} for row in rows]


def write_plan(path, rows):
    with open(path,'w',encoding='utf-8') as stream:
        json.dump(build_plan(rows),stream,ensure_ascii=False)
