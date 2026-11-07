import json,datetime,zoneinfo
def j(f): return json.dumps(json.load(open(f)),ensure_ascii=False).replace('</','<\\/')
t=open('template.html').read()
for k,f in [('__EVENTS__','events.json'),('__BARS__','bars.json'),('__GIVE__','give.json'),('__DRIVES__','drives.json'),('__MEALS__','meals.json'),('__HMEALS__','hmeals.json'),('__CATS__','cats.json')]:
    t=t.replace(k,j(f))
t=t.replace('__UPDATED__',(lambda d:d.strftime('%b ')+str(d.day)+d.strftime(', %Y'))(datetime.datetime.now(zoneinfo.ZoneInfo('America/Los_Angeles'))))
open('index.html','w').write(t)
assert '—' not in t, 'em dash in output'
print('built', len(t), 'bytes')
