"""Task-conditioned literal evidence selection; no answer-key access or model calls."""
import hashlib,re


def compile_view(raw,request,max_bytes=6000):
 terms=set(re.findall(r'[a-z][a-z0-9_]{3,}',request.lower()))
 lines=raw.splitlines(keepends=True);selected=[];used=0;matched=0
 for i,line in enumerate(lines,1):
  text=line.decode('utf-8',errors='strict')
  if terms.intersection(re.findall(r'[a-z][a-z0-9_]{3,}',text.lower())):
   matched+=1
   if used+len(line)<=max_bytes:
    selected.append({'line':i,'text':text});used+=len(line)
 return {'schema':'helix.literal_query.v1','source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'coverage':'partial literal matches to request; omitted evidence remains in test.log; retrieve if needed','matching_lines':matched,'omitted_matching_lines':matched-len(selected),'lines':selected}
