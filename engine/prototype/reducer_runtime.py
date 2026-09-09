"""Versioned conservative command presentation; execute once, never retry here.

Caller injects only result['visible']; accounting and exact refs stay available.
Native passthrough is a lossless JSON transport, not a shell-string rewrite.
"""
import base64
import json
from pathlib import Path
import time

import evidence
import verification

VERSION='helix.reducers.v1'


def encode(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


def body(raw):
    try:return {'text':raw.decode('utf-8')}
    except UnicodeDecodeError:return {'base64':base64.b64encode(raw).decode('ascii')}


def choose(argv):
    """Known producer/argument subset. Unknown or shell-wrapped calls bypass."""
    name=Path(argv[0]).name
    args=argv[1:]
    if name in ('python','python3') and args[:2]==['-m','pytest']:
        name='pytest';args=args[2:]
    if name in ('pytest','pytest-3'):
        allowed={'-q','-qq','-v','-vv','-x','--disable-warnings','--no-header','--tb=short','--tb=long','--tb=auto'}
        if all(a in allowed or not a.startswith('-') for a in args):return 'pytest'
    if name in ('gcc','g++','clang','clang++'):
        # Explicit text diagnostics only; no JSON/custom diagnostic formats.
        if not any('diagnostic-format' in a or 'diagnostics-format' in a for a in args):return 'compiler'
    return None


def validate_policy(enabled=True,format_hint=None,max_bytes=6000,minimum_saving_bytes=128,minimum_saving_fraction=0.05):
    if type(enabled) is not bool:raise ValueError('Boolean switch required')
    if type(minimum_saving_bytes) is not int or minimum_saving_bytes<0:raise ValueError('Invalid byte gate')
    if not isinstance(minimum_saving_fraction,(int,float)) or isinstance(minimum_saving_fraction,bool) or not 0<=minimum_saving_fraction<=1:raise ValueError('Invalid fraction gate')
    if format_hint not in (None,'pytest','compiler'):raise ValueError('Unknown declared producer format')
    if type(max_bytes) is not int or max_bytes<1400:raise ValueError('Invalid packet budget')


def present(store,receipt,*,enabled=True,format_hint=None,max_bytes=6000,
            minimum_saving_bytes=128,minimum_saving_fraction=0.05):
    started=time.perf_counter();before=dict(store.metrics)
    validate_policy(enabled,format_hint,max_bytes,minimum_saving_bytes,minimum_saving_fraction)
    command=store.receipt(receipt)
    stdout=store.get(command['stdout']['sha256']);stderr=store.get(command['stderr']['sha256'])
    if len(stdout)!=command['stdout']['bytes'] or len(stderr)!=command['stderr']['bytes']:raise ValueError('Raw evidence length mismatch')
    native={'schema':'helix.native_output.v1','receipt':receipt,'exit_code':command['exit_code'],
        'timed_out':command['timed_out'],'interrupted':command.get('interrupted',False),
        'stdout':body(stdout),'stderr':body(stderr)}
    native_bytes=len(encode(native));visible=native;mode='native';reason='disabled' if not enabled else 'unsupported producer'
    kind=format_hint or choose(command['argv'])
    error=None;candidate_bytes=None
    if enabled and kind:
        if native_bytes<minimum_saving_bytes+1400:reason='small output'
        else:
            try:
                candidate=evidence.packet(store,receipt,kind,max_bytes)
                verification.verify(store,candidate)
                candidate_bytes=len(encode(candidate))
                gain=native_bytes-candidate_bytes
                if gain>=minimum_saving_bytes and gain>=minimum_saving_fraction*native_bytes:
                    visible=candidate;mode='reduced';reason='verified partial projection'
                else:reason='insufficient representation gain'
            except (ValueError,TypeError,KeyError,UnicodeError,RuntimeError) as exc:
                reason='reducer failed; captured result retained';error=type(exc).__name__+': '+str(exc)
    result={'schema':VERSION,'mode':mode,'reason':reason,'kind':kind,'command_receipt':receipt,
        'visible':visible,'error':error,'measurements':{'raw_bytes':len(stdout)+len(stderr),
            'native_transport_bytes':native_bytes,'candidate_projection_bytes':candidate_bytes,
            'visible_transport_bytes':len(encode(visible)),'seconds':time.perf_counter()-started,
            'store_io':{k:store.metrics[k]-before[k] for k in before},
            'scope':'JSON presentation bytes, not native model tokens. Caller overhead and physical I/O excluded.'}}
    # The full decision is cold evidence; never silently discard a failure reason.
    result['decision_receipt']=store.put(encode(result))['sha256']
    return result


def execute(store,argv,cwd,environment_id,*,enabled=True,format_hint=None,timeout=None,watch=(),env=None,**admission):
    if not isinstance(argv,list) or not argv or any(not isinstance(a,str) or '\x00' in a for a in argv):raise ValueError('Explicit argv list required')
    # Validate policy before any command side effects.
    validate_policy(enabled=enabled,format_hint=format_hint,**admission)
    start=time.perf_counter();before=dict(store.metrics)
    receipt=evidence.capture(store,argv,cwd,environment_id,timeout,watch,env)
    result=present(store,receipt,enabled=enabled,format_hint=format_hint,**admission)
    result['execution']={'seconds':time.perf_counter()-start,
        'store_io':{k:store.metrics[k]-before[k] for k in before},'underlying_executions':1}
    return result
