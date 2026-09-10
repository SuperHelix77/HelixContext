"""Independent offline witnesses; never supplied to the pilot models."""
import importlib.util
import json
from pathlib import Path
import sys

def check(path):
    spec=importlib.util.spec_from_file_location("candidate", path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    outcomes={}
    c=m.Cache(); c.put("x",None,now=2,ttl=3)
    outcomes["expiry_equality"]=c.get("x",now=5,default="absent")=="absent"
    c=m.Cache(); c.put("x",8,now=0,ttl=7)
    outcomes["batch_multiplicity"]=c.get_many(["x","missing","x","missing"],now=1,default=-1)==[8,-1,8,-1]
    before=dict(c.entries)
    try: c.get_many(["x", ""],now=8)
    except ValueError: outcomes["invalid_batch"]=c.entries==before
    else: outcomes["invalid_batch"]=False
    outcomes["read_no_mutation"]=c.get_many(["x"],now=8)==[None] and c.entries==before
    outcomes["live_falsey"]=True
    for i,value in enumerate([None,False,0,[],{}]):
        c.put(str(i),value,now=0,ttl=10)
        outcomes["live_falsey"] &= c.get_many([str(i)],now=1,default="absent")==[value]
    return outcomes

if __name__=="__main__": print(json.dumps(check(Path(sys.argv[1]))))
