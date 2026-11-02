import json,re,sys
# Reads a dump of the 'Christmas Pop Up Bars' tab (get_values JSON) and writes bars.json.
# Columns: B name, C date, E time, F location, G area, I vibe, L top pick, M status (2026), N source.
rows=json.load(open(sys.argv[1]))['values'][1:]
REGION=eval(open('build_data.py').read().split("REGION=")[1].split("\nA2R")[0])
A2R={a:r for r,l in REGION.items() for a in l}
FIX={'Skal Beeer Hall':'Skal Beer Hall','Miracle on 2nd (Miracle)':'Miracle on 2nd','Gingerbread Rooftop Pop-Up (Lotte)':'Gingerbread Rooftop Pop-Up','Kringle’s Filling Station':'Kringle’s Filling Station'}
AREA={'Seattle (TBA)':'Downtown'}
VIBE={'Skal Beer Hall':'Viking beer hall in holiday mode','The Pine Box':'Holiday-decked beer hall in an old funeral home','Home Alone pop-up':'Home Alone themed holiday bar','Home Alone':'Home Alone themed holiday bar','Busy Body':'Tacoma holiday pop-up','Otter on the Rocks':'West Seattle holiday pop-up','Jollidaze':'Holiday-decorated cafe','Hood Famous Cafe & Bar':'Holiday-themed drinks and treats','Pike Place Bar & Grill':'Holiday-decorated bar and grill','Hood Famous Cafe & Bar':'Holiday-themed drinks and treats at the Filipino bakery','Jolly':'Holiday pop-up at the casino'}
def clean(s):
    s=re.sub(r'\s*\((?:[^()]*(?:CHS|Xmas Pop-Up Bars|Reddit|Rosebay|Edgewater|Rob Roy|Visit Seattle|Charlotte|Emerald Palate|Aluel|Kamp|Christmas Dive Bar|La Palmera|Elf Bar|S E A T T L E|Fabulous|per )[^()]*)\)','',s)
    s=re.sub(r'\s+(PURPLE CAF\S* & WINE BAR(\+1)?|Secret Seattle\+1|WOODEN CITY.*)$','',s)
    s=re.sub(r'(\d|am|pm)\s*–\s*',lambda m:m.group(1)+' to ',s)
    return re.sub(r'\s*[–—]\s*',', ',s).replace('  ',' ').strip(' .')
out=[]
for r in rows:
    r=r+['']*14
    n=r[1].strip()
    if not n: continue
    st=r[12].strip()
    if st.upper().startswith('CLOSED') or not r[6].strip() or not r[5].strip(): continue
    a=AREA.get(r[6].strip(),r[6].strip())
    if a not in A2R: print('no region for',a,n); continue
    ok=bool(re.match(r'^(Confirmed|Listed for 2026)',st))
    out.append(dict(n=FIX.get(n,n),w=clean(r[2]),tm=clean(r[4]),loc=clean(r[5]),a=a,r=A2R[a],v=(lambda x:x if len(x)>20 else VIBE.get(FIX.get(n,n),x))(clean(r[8])),
                    p=r[11].strip().lower().startswith('y'),ok=ok))
json.dump(out,open('bars.json','w'),ensure_ascii=False);print(len(out),'bars;',sum(b['p'] for b in out),'picks;',sum(b['ok'] for b in out),'confirmed')
