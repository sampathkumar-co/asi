from __future__ import annotations

from itertools import combinations
from typing import Any

from .registry import ToolResult

def subset_optimize(payload: dict[str, Any]) -> ToolResult:
    try:
        items=payload.get('items')
        capacity=float(payload.get('capacity'))
        if not isinstance(items,list) or not items or len(items)>22 or capacity<0:
            raise ValueError('items must contain 1..22 entries and capacity must be nonnegative')
        clean=[]
        names=set()
        for row in items:
            if not isinstance(row,dict): raise ValueError('each item must be an object')
            name=str(row.get('name',''))
            weight=float(row.get('weight'))
            value=float(row.get('value'))
            if not name or name in names or weight<0:
                raise ValueError('item names must be unique and weights nonnegative')
            names.add(name); clean.append((name,weight,value))
        constraints=payload.get('constraints',{})
        if not isinstance(constraints,dict): raise ValueError('constraints must be an object')
        implies=constraints.get('implies',[])
        exclusive=constraints.get('exclusive',[])
        if not isinstance(implies,list) or not isinstance(exclusive,list): raise ValueError('implies/exclusive must be arrays')
        def pairs(raw,label):
            out=[]
            for pair in raw:
                if not isinstance(pair,(list,tuple)) or len(pair)!=2: raise ValueError(f'{label} entries must be pairs')
                a,b=str(pair[0]),str(pair[1])
                if a not in names or b not in names: raise ValueError(f'{label} references unknown item')
                out.append((a,b))
            return out
        implies=pairs(implies,'implies'); exclusive=pairs(exclusive,'exclusive')
        valid=[]
        n=len(clean)
        for r in range(n+1):
            for combo in combinations(clean,r):
                chosen={x[0] for x in combo}
                weight=sum(x[1] for x in combo)
                if weight>capacity: continue
                if any(a in chosen and b not in chosen for a,b in implies): continue
                if any(a in chosen and b in chosen for a,b in exclusive): continue
                value=sum(x[2] for x in combo)
                valid.append((value,weight,tuple(sorted(chosen))))
        if not valid: raise ValueError('no valid subset')
        best_value=max(v[0] for v in valid)
        best=[v for v in valid if v[0]==best_value]
        if bool(payload.get('require_unique',True)) and len(best)!=1:
            raise ValueError('optimal subset is not unique')
        value,weight,chosen=min(best,key=lambda x:x[2])
        def num(x):
            return str(int(x)) if float(x).is_integer() else str(x)
        sep=str(payload.get('item_separator',''))
        items_s=sep.join(chosen)
        template=str(payload.get('answer_template','FINAL: {value} | {items}'))
        answer=template.replace('{value}',num(value)).replace('{weight}',num(weight)).replace('{items}',items_s)
        if '{' in answer or '}' in answer: raise ValueError('answer_template contains unresolved placeholders')
        if not answer.lstrip().upper().startswith('FINAL:'): answer='FINAL: '+answer.strip()
        checks={'capacity_respected':weight<=capacity,'all_constraints_hold':True,'global_optimum_verified':True,'unique_optimum':len(best)==1}
        return ToolResult(True,output={'answer':answer,'checks':checks,'evidence':{'value':value,'weight':weight,'items':list(chosen),'valid_subset_count':len(valid),'optimal_count':len(best)}})
    except Exception as exc:
        return ToolResult(False,error=str(exc))
