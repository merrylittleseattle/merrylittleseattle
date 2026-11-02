import json,re
D='/tmp/claude-tool-results/8f5a280f-1cb1-529f-803e-4141b9d2f05f/'
import sys
rows=json.load(open(sys.argv[1]))['values'][1:]
ok=re.compile(r'^(Confirmed|Listed for 202[67]|Returning 2026|Announced|Year-round|Ongoing|Season-dependent)')
sec=None;out=[];secs=[]
for r in rows:
    r=r+['']*(20-len(r))
    if r[0].strip():
        sec=r[0].strip()
        if 'PLEASE KEEP' in sec: break
        secs.append(sec)
        continue
    if not r[1].strip(): continue
    if ok.match(r[12].strip()):
        out.append(dict(section=sec,name=r[1],datetext=r[2],dates=r[3],time=r[4],loc=r[5],area=r[6],type=r[7],vibe=r[8],res=r[11],status=r[12],link=r[13],pick=r[14],tags=r[15],tk=r[15],tf=r[16],ta=r[17],td=r[18],tr=r[19]))
json.dump(out,open('raw.json','w'),indent=1); json.dump(secs,open('sections.json','w')); print(len(out))
