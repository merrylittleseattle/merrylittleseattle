import json,re
o=json.load(open('raw.json'))
DAYTRIP_SECS={'Edmonds','South','East','Bainbridge','Vashon','Whidbey','Orcas','Orcas Island','Camano','Camano Island','San Juan Island','Kitsap & Peninsula','Oregon','Vancouver','Islands (And West)'}
REGION={
 'North Seattle':['Green Lake','Ballard','Fremont','Phinney Ridge','Magnuson Park','Laurelhurst','Northgate','UW / Arboretum','University District','Wallingford','Magnolia','Queen Anne','Lake Union','Carkeek Park','Matthews Beach','Sand Point','Ravenna','UW','Northeast Seattle','Greenwood','Interbay','Lower Queen Anne','Sunset Hill'],
 'Central Seattle':['Downtown','Seattle Center','Capitol Hill','First Hill','Waterfront','Belltown','Central District','International District','Madison Park','Madrona','Downtown / Seattle Center','Seattle','Pioneer Square','South Lake Union','Uptown','Little Saigon','Chinatown'],
 'South & West Seattle':['West Seattle','White Center','South Park','SoDo','Georgetown','Rainier Valley','Rainier Beach','Burien','Mount Baker','Seward Park','Columbia City','Tukwila','Beacon Hill','Highland Park'],
 'North of Seattle':['Edmonds','Shoreline','Lynnwood','Bothell','Everett','Tulalip','Woodinville','Mukilteo','Kenmore','Lake Forest Park'],
 'Eastside':['Bellevue','Redmond','Kirkland','Issaquah','Sammamish','Carnation','Snoqualmie','Renton','Medina','Yarrow Point','Mercer Island'],
 'South Sound':['Tacoma','Federal Way','Puyallup','Spanaway Park','Chehalis','Elbe','Des Moines','Olympia','Lacey','Kent','University Place','Eatonville'],
 'Mountains':['Snoqualmie Pass','Leavenworth','Mt. Rainier','Mt Hood'],
 'Islands & Peninsula':['Bainbridge Island','Vashon Island','San Juan Island','Poulsbo','Port Townsend','Bremerton','Camano Island'],
 'Farther Afield':['Oregon','Vancouver'],
}
A2R={a:r for r,l in REGION.items() for a in l}
SRC=r'\((?:[^()]*?(?:Facebook|EverOut|AllEvents|listing|screenshot|ticket sites|L[a]ra|Seattle\'s Child|ParentMap|BroadwayWorld|Fever\b)[^()]*)\)'
def clean(s):
    s=s or ''
    s=re.sub(SRC,'',s)
    s=re.sub(r';\s*(replaces|Elf not)[^)]*','',s)
    s=re.sub(r'\(\s*\)','',s)
    s=s.replace(' — ',': ' if False else ', ').replace('—',', ')
    s=re.sub(r'\s*\+\d[^+]*\+\d','',s); s=re.sub(r'\+\d\b','',s)
    for junk in [' purchase.vashoncenterforthearts.org','purchase.vashoncenterforthearts.org',' Bainbridge Island Museum of Art',' SJI Winterfest']: s=s.replace(junk,'')
    s=re.sub(r'\s-\+','',s); s=re.sub(r'\bRunSignu\w*','',s)
    s=re.sub(r'\s+',' ',s).strip(' ;,-')
    return s
FREE_NAMES=[x.lower() for x in ['Westlake Tree Lighting','Westlake Park Holiday Carousel','Holiday in the Park (Volunteer Park)','Festival of Trees (Fairmont','Meadowbrook Luminaria','Ballard Light Walk','Ballard Neighborhood Lighting','Ballard HolidayFest','Evergreen Church','Clam Lights','Seattle Center Winterfest','Pike Place Holiday Night Market','Pike Place Magic','Renegade Craft Fair','PhinneyWood Winter Festival','Woodinville Winterfest','Magnolia Holiday Market','Ballard Makers Market','Arboretum Winter Market','Winterfest Train','Ice Sculpting','Gingerbread Village','Teddy Bear Suite','Figgy Pudding','Holiday Bookfest','Firepit Socials','Tomte Trail','Free First Thursday','Free Third Saturday','Fremont Freezes Over','Lake City Winterfest','Candy Cane Lane','Pathway of Lights','Twinkle Twinkle','Festive Lights Across Downtown','Winterfest – Tree Lighting','Let It Glow','Snoqualmie Winter Lights']]
KIDS=r'\bkids?\b|\bfamil(y|ies)\b|children|all ages|all-ages|toddler|tots?\b|story ?time|photos with santa|santa photos|breakfast with santa|polar express|letters to santa|teddy bear'
DTGROUP={'Edmonds':'North: Edmonds and up the coast','South':'South: Tacoma and the South Sound','East':'East: Snoqualmie, Leavenworth and the mountains','Islands (And West)':'Islands','Bainbridge':'Islands','Vashon':'Islands','Whidbey':'Islands','Orcas':'Islands','Orcas Island':'Islands','Camano':'Islands','Camano Island':'Islands','San Juan Island':'Islands','Kitsap & Peninsula':'Kitsap and the Olympic Peninsula','Oregon':'Oregon','Vancouver':'Vancouver, BC'}
EXCL=re.compile(r'cut off',re.I)
out=[]
for i,e in enumerate(o):
    if EXCL.search(e['datetext']+e['vibe']): continue
    area=re.sub(r'\s*\(day trip\)','',e['area']).strip() or 'Seattle'
    reg=A2R.get(area)
    if not reg: print('NOREGION',area,e['name'])
    dates=re.findall(r'\d\d/\d\d',e['dates'] or '')
    iso=[]
    for d in dates:
        m,dd=int(d[:2]),int(d[3:])
        y=2027 if m<6 else 2026
        iso.append(f'{y}-{m:02d}-{dd:02d}')
    sec=e['section']
    cat='Day Trips' if sec in DAYTRIP_SECS else sec
    vibe=re.sub(r'\s*\(see the [^)]*tab\)','',clean(e['vibe']))
    blob=(e['vibe']+' '+e['datetext']).lower()
    tags=[]
    # "kids 6 and under free", "free for members" and the like do not make the event free
    blob_free=re.sub(r'(\d+\s*(and|&|or)\s*(under|younger)|under\s*\d+|ages?\s*\d+\s*(and|&|or)\s*(under|younger)|kids?|children|members|toddlers|babies|infants|seniors|veterans)\W+(\w+\W+){0,2}free\b|\bfree\s+(for|to)\s+(kids|children|members|seniors|ages|those|anyone under)|\bfree\s+with\s+\w+|\bfree\s+(parking|shuttle|wifi|coffee|cocoa|hot chocolate|gift|refills?)\b','',blob)
    if re.search(r'\bfree\b',blob_free) and not re.search(r'\$\s*\d|tickets? from|admission \$',blob): tags.append('Free')
    if re.search(r'ticket|\bbook|reserv|rsvp|register|buy|sells? out',(e['res']+' '+e['datetext']).lower()): tags.append('Book ahead')
    if 'Free' in tags and '$' in e['datetext']: tags.remove('Free')
    nmL=e['name'].lower(); blobL=(e['name']+' '+e['datetext']+' '+e['vibe']).lower()
    if 'Free' not in tags and '$' not in e['datetext'] and (any(k in nmL for k in FREE_NAMES) or re.search(r'residential display|tree lighting|shore viewing|menorah lighting|free admission|free to (attend|watch|view)',blobL)):
        tags.append('Free')
    auto_free=list(tags)
    has=lambda k: bool((e.get(k) or '').strip()) and not (e.get(k) or '').strip().lower().startswith('no')
    mine=any((e.get(k) or '').strip() for k in ('tk','tf','ta','td','tr'))
    if mine:
        tags=[]
        if has('tf') or (not (e.get('tf') or '').strip() and 'Free' in auto_free): tags.append('Free')
        if has('tr'): tags.append('Book ahead')
        adult=has('ta')
        if adult: tags.append('For adults')
        if has('td'): tags.append('For dogs')
        if (has('tk') or e['section']=='Kids') and not adult: tags.append('For kids')
    else:
        adult=bool(re.search(r'\b21\+|18\+|adults only|grown-ups',e['name']+' '+e['datetext']+' '+e['vibe'],re.I))
        if adult: tags.append('For adults')
        if re.search(r'\bdog|pup|pet\b|paws|howl',(e['name']+' '+e['section']).lower()): tags.append('For dogs')
        kid=e['section']=='Kids' or re.search(KIDS,(e['name']+' '+e['vibe']+' '+e['datetext']).lower())
        if kid and not adult and not re.search(r'gala|illuminating the dark',e['name'].lower()): tags.append('For kids')
    if re.search(r'livestream: yes|livestreamed|livestream available|watch online',e['vibe'].lower()): tags.append('Livestream')
    link=e['link'].strip() if e['link'].strip().startswith('http') else ''
    nm=re.sub(r'\s+—\s+',': ',e['name'])
    out.append(dict(id=i,n=clean(nm),c=cat,t=e['type'] or 'Other',dt=clean(e['datetext']),d=iso,tm=clean(e['time']).strip('—- '),loc=clean(e['loc']),a=area,r=reg or 'Central Seattle',v=vibe,g=tags,u=link,sg=DTGROUP.get(sec,''),p=1 if (e.get('pick') or '').strip().lower().startswith('y') else 0))
for k,s in enumerate(json.load(open('ships.json'))):
    out.append(dict(id=10000+k,n=s['n'],c='Boats',t='Boat',dt=s['dt'],d=s['d'],tm=s['tm'],loc=s['loc'],a=s['a'],r=A2R.get(s['a'],'Central Seattle'),v=s['v'],g=['Free'],u=s['u'],p=0))
json.dump(out,open('events.json','w'))
secs=[]
for s in json.load(open('sections.json')):
    s='Day Trips' if s in DAYTRIP_SECS else s
    if s not in secs: secs.append(s)
json.dump(secs,open('cats.json','w'))
print(len(out))
