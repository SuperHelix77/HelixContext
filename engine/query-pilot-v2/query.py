"""Task-conditioned literal evidence selection; no answer-key access or model calls."""
import hashlib,re


def terms(text):
 # Keep exact compound identifiers and also index their components.
 words=set(re.findall(r'[a-z][a-z0-9_]{3,}',text.lower()))
 return words | {part for word in words for part in word.split('_') if len(part)>=4}


def compile_view(raw,request,max_bytes=6000):
 query_terms=terms(request)
 lines=raw.splitlines(keepends=True);selected=[];used=0;matched=0
 for i,line in enumerate(lines,1):
  text=line.decode('utf-8',errors='strict')
  if query_terms.intersection(terms(text)):
   matched+=1
   if used+len(line)<=max_bytes:
    selected.append({'line':i,'text':text});used+=len(line)
 return {'schema':'helix.literal_query.v2','source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'coverage':'partial literal matches to request; omitted evidence remains in test.log; retrieve if needed','matching_lines':matched,'omitted_matching_lines':matched-len(selected),'lines':selected}
