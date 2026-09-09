"""Experimental lossless JSON table transport; no semantic record filtering."""
from decision_packet import verify_metadata,encode,parse
from verification import exact_value


def table(store,view):
    verify_metadata(store,view)
    result={'fields':view['fields'],'rows':[[row[k] for k in view['fields']] for row in view['metadata']]}
    restored=expand(parse(encode(result)))
    if not exact_value(restored,view['metadata']):raise ValueError('JSON table roundtrip changed values or types')
    return result


def expand(value):
    if not isinstance(value,dict) or set(value)!={'fields','rows'}:raise ValueError('Invalid table')
    fields=value['fields'];rows=value['rows']
    if not isinstance(fields,list) or not fields or any(not isinstance(k,str) or not k for k in fields) or len(set(fields))!=len(fields):raise ValueError('Invalid fields')
    if not isinstance(rows,list) or any(not isinstance(row,list) or len(row)!=len(fields) for row in rows):raise ValueError('Invalid rows')
    return [dict(zip(fields,row)) for row in rows]
