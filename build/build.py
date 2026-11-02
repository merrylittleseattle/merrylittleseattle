import json
def j(f): return json.dumps(json.load(open(f)),ensure_ascii=False).replace('</','<\\/')
t=open('template.html').read()
for k,f in [('__EVENTS__','events.json'),('__BARS__','bars.json'),('__GIVE__','give.json'),('__DRIVES__','drives.json'),('__MEALS__','meals.json'),('__CATS__','cats.json')]:
    t=t.replace(k,j(f))
t=t.replace('__UPDATED__','Nov 1, 2026')
open('index.html','w').write(t)
print('ok', '—' in t)
