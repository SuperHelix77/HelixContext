import json,subprocess,selectors,time,os
from pathlib import Path
CLI='/Applications/ChatGPT.app/Contents/Resources/codex'
class Client:
 def __init__(self,overrides=()):
  self.log=open(Path(__file__).parent/'rpc-stderr.txt','w')
  self.p=subprocess.Popen([CLI,'app-server','--stdio',*sum((['-c',x] for x in overrides),[])],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,bufsize=0)
  self.sel=selectors.DefaultSelector();self.sel.register(self.p.stdout,selectors.EVENT_READ);self.next=0;self.events=[];self.buffer=b""
  self.call('initialize',{'clientInfo':{'name':'helix-validation','version':'0.1'},'capabilities':{'experimentalApi':True}})
  self.p.stdin.write((json.dumps({'method':'initialized'})+'\n').encode());self.p.stdin.flush()
 def read(self,timeout=30):
  while b'\n' not in self.buffer:
   if not self.sel.select(timeout):raise TimeoutError('RPC timeout')
   block=os.read(self.p.stdout.fileno(),65536)
   if not block:raise RuntimeError('RPC closed')
   self.buffer+=block
  line,self.buffer=self.buffer.split(b'\n',1);return json.loads(line)
 def call(self,method,params):
  self.next+=1;rid=self.next;self.p.stdin.write((json.dumps({'id':rid,'method':method,'params':params})+'\n').encode());self.p.stdin.flush()
  while True:
   x=self.read()
   if x.get('id')==rid:
    if 'error' in x:raise RuntimeError(x['error'])
    return x['result']
   self.events.append(x)
 def close(self):self.p.terminate();self.p.wait(timeout=10);self.log.close()
