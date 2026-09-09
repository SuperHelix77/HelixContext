"""Exact event identifier resolution. No semantic correction or fuzzy matching."""
import json

def resolve(decision,raw):
 events=[json.loads(l)['event'] for l in raw.splitlines()]
 ids={};turns=set()
 for e in events:
  if e['event_id'] in ids or e['turn'] in turns:raise ValueError('ambiguous archive identities')
  ids[e['event_id']]=e['turn'];turns.add(e['turn'])
 def one(value):
  if type(value) is int and value in turns:return value
  if type(value) is str and value in ids:return ids[value]
  raise ValueError('unbound exact event reference')
 out=dict(decision);out['policy']=one(out['policy'])
 for key in ('amendments','rejected'):
  if type(out[key]) is not list:raise ValueError('reference list required')
  out[key]=[one(x) for x in out[key]]
 return out

def test():
 raw=b'{"event":{"turn":1,"event_id":"E01"}}\n{"event":{"turn":17,"event_id":"E17"}}\n'
 d={'policy':'E01','amendments':['E17'],'rejected':[],'authorized':False,'reason':'X'}
 assert resolve(d,raw)=={**d,'policy':1,'amendments':[17]}
 assert d['policy']=='E01'
 for bad in ('E1','e01','E99',True,1.0):
  try:resolve({**d,'policy':bad},raw)
  except ValueError:pass
  else:raise AssertionError('inexact reference accepted')
 try:resolve(d,raw+raw)
 except ValueError:pass
 else:raise AssertionError('ambiguous reference accepted')
if __name__=='__main__':test();print('Exact identity adapter checks PASS')
