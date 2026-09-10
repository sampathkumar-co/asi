from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from .python_compute import _sanitize
from .registry import ToolResult

_TIMEOUT_SECONDS = 2.0
_RUNNER = r"""
import json, sys
from collections import defaultdict, deque
from heapq import heappush, heappop
from itertools import permutations, combinations, product
printed=[]
def capture_print(*args, **kwargs):
    if kwargs:
        raise ValueError('python_trace print kwargs are unsupported')
    printed.append([str(x) for x in args])
SAFE={
 'abs':abs,'all':all,'any':any,'bool':bool,'dict':dict,'enumerate':enumerate,
 'float':float,'int':int,'len':len,'list':list,'max':max,'min':min,'range':range,
 'reversed':reversed,'round':round,'set':set,'sorted':sorted,'str':str,'sum':sum,
 'tuple':tuple,'zip':zip,'defaultdict':defaultdict,'deque':deque,'heappush':heappush,
 'heappop':heappop,'permutations':permutations,'combinations':combinations,
 'product':product,'print':capture_print
}
payload=json.loads(sys.stdin.read())
ns={'__builtins__':SAFE}
exec(payload['code'],ns,ns)
print(json.dumps({'prints':printed},ensure_ascii=False,separators=(',',':')))
"""

def python_trace(payload: dict[str, Any]) -> ToolResult:
    try:
        code = str(payload.get('code',''))
        if not code:
            raise ValueError('code is required')
        safe_code = _sanitize(code)
        proc = subprocess.run([sys.executable,'-I','-S','-c',_RUNNER], input=json.dumps({'code':safe_code}), capture_output=True, text=True, timeout=_TIMEOUT_SECONDS, check=False)
        if proc.returncode != 0:
            err=(proc.stderr or proc.stdout or 'python_trace failed').strip()
            return ToolResult(False,error=err[-1000:])
        data=json.loads(proc.stdout)
        prints=data.get('prints',[])
        if not isinstance(prints,list) or not prints:
            raise ValueError('code produced no print output')
        select=int(payload.get('print_index',-1))
        if (select >= len(prints) or select < -len(prints)) and len(prints) == 1:
            select = -1
        if select >= len(prints) or select < -len(prints):
            raise ValueError('print_index out of range')
        args=prints[select]
        if not isinstance(args,list):
            raise ValueError('captured print output invalid')
        sep=str(payload.get('separator',' | '))
        answer='FINAL: '+sep.join(str(x) for x in args)
        checks={'executed_exact_source':True,'print_captured':True,'selected_print_exists':True}
        return ToolResult(True,output={'answer':answer,'checks':checks,'evidence':{'prints':prints,'selected_index':select}})
    except subprocess.TimeoutExpired:
        return ToolResult(False,error='python_trace timed out')
    except Exception as exc:
        return ToolResult(False,error=str(exc))
