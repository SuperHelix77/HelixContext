import subprocess
import sys
import astra_patch_pair as pair


def test_checker_rejects_original_and_accepts_transactional_implementation(tmp_path):
    root,m,prompts=pair.prepare(tmp_path/'pair')
    target=root/'tasks/off/queue_state.py'
    assert subprocess.run([sys.executable,str(root/'checker.py'),str(target)],capture_output=True).returncode!=0
    target.write_text('''class Queue:
    def __init__(self): self.items=[];self.cursor=0
    def append_batch(self,values):
        pending=[]
        for value in values:
            if type(value) is not int or value<0:raise ValueError('invalid')
            pending.append(value)
        self.items.extend(pending)
        self.cursor+=len(pending)
        return self.cursor
''')
    assert subprocess.run([sys.executable,str(root/'checker.py'),str(target)],capture_output=True).returncode==0
    assert m['preflight']['exit_code']!=0 and m['max_calls']==2
    assert '$helixcontext' in prompts['on'] and '$helixcontext' not in prompts['off']
    for name in m['sources']:
        if name!='queue_state.py':assert (root/'tasks/off'/name).read_bytes()==(root/'tasks/on'/name).read_bytes()
