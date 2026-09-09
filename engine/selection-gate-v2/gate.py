"""Prospective exact-artifact evaluator. No model call or compression policy."""
import hashlib,json

def sha(raw):return hashlib.sha256(raw).hexdigest()

def fixture():
    def row(group,revision,approved=True,published=True,expiry=30,**extra):
        return dict(id=f'{group}:{revision}',group=group,revision=revision,approved=approved,published=published,expires_day=expiry,amount_text='000.050',payload='café / cafe\u0301 / Ω /  two spaces\tend',**extra)
    # Deliberate reverse/interleaved source order; group sorting is not source order.
    records=[row('H',2),row('A',1),row('B',1),row('C',1),row('D',1),row('E',1),row('F',1,published=False),row('G',1,expiry=25),row('A',2,approved=False),row('B',2,expiry=24),row('C',2,approved='true'),row('D',2,published='true'),row('E',2,published=False),row('H',1),row('I',1,approved=1),row('J',1,published=1)]
    # Vary valid JSON serialization and newline bytes to expose reserialization.
    return b''.join((json.dumps(r,ensure_ascii=(i%2==0),separators=(', ', ': ') if i%3 else (',',':'))+ ('\r\n' if i%2 else '\n')).encode() for i,r in enumerate(records))

# Fixed independent expected identity list, not computed using candidate algorithm.
EXPECTED_IDS=('D:1','E:1','G:1','H:2')

def expected(source):
    by_id={json.loads(line)['id']:line for line in source.splitlines(keepends=True)}
    return b''.join(by_id[key] for key in EXPECTED_IDS)


def grade(original,current,artifact):
    bound=sha(original)==sha(fixture())
    return {'source_bound':bound,'artifact_exact':artifact==expected(original),'source_unchanged':current==original,'accepted':bound and artifact==expected(original) and current==original,'expected_sha256':sha(expected(original)),'observed_sha256':sha(artifact)}


def reference(source):
    """Reference implementation used only as a positive control."""
    latest={}
    for line in source.splitlines(keepends=True):
        r=json.loads(line)
        if r['published'] is True and (r['group'] not in latest or r['revision']>latest[r['group']][0]['revision']):latest[r['group']]=(r,line)
    return b''.join(line for group,(r,line) in sorted(latest.items()) if r['approved'] is True and r['expires_day']>=25)


def mutant(source,mode):
    rows=[(json.loads(line),line) for line in source.splitlines(keepends=True)]
    if mode=='filter_before_latest':rows=[(r,l) for r,l in rows if r['approved'] is True and r['expires_day']>=25]
    latest={}
    for r,line in rows:
        published=bool(r['published']) if mode=='truthy_published' else r['published']==True if mode=='equal_published' else r['published'] is True
        if published and (r['group'] not in latest or r['revision']>latest[r['group']][0]['revision']):latest[r['group']]=(r,line)
    selected=[]
    for group,(r,line) in sorted(latest.items()):
        approved=bool(r['approved']) if mode=='truthy_approved' else r['approved']==True if mode=='equal_approved' else r['approved'] is True
        unexpired=r['expires_day']>25 if mode=='exclusive_expiry' else r['expires_day']>=25
        if approved and unexpired:selected.append((r,line))
    if mode=='reverse_order':selected.reverse()
    if mode=='reserialize':return b''.join((json.dumps(r)+'\n').encode() for r,line in selected)
    if mode=='normalize_newlines':return b''.join(line.replace(b'\r\n',b'\n') for r,line in selected)
    if mode=='drop_final_newline':return b''.join(line for r,line in selected).rstrip(b'\r\n')
    return b''.join(line for r,line in selected)

MUTATIONS=('filter_before_latest','truthy_published','equal_published','truthy_approved','equal_approved','exclusive_expiry','reverse_order','reserialize','normalize_newlines','drop_final_newline')

if __name__=='__main__':
    source=fixture()
    result={'scope':'Evaluator mutation testing, not model capability evidence','source_sha256':sha(source),'expected_sha256':sha(expected(source)),'positive_control':grade(source,source,reference(source)),'mutations':{mode:grade(source,source,mutant(source,mode)) for mode in MUTATIONS},'source_mutation':grade(source,source+b' ',expected(source))}
    assert result['positive_control']['accepted']
    assert all(not r['accepted'] for r in result['mutations'].values()) and not result['source_mutation']['accepted']
    print(json.dumps(result,indent=2))
