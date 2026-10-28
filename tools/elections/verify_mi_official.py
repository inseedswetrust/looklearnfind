import re,json,unicodedata
L=[l.strip() for l in open('data/elections/MI/captures/boe_text.txt',encoding='utf-8')]
race=None;party=None;off={}
i=0
PARTY=re.compile(r'(Party|Affiliation)$')
while i<len(L):
    l=L[i]
    m=re.match(r'(?:(\d+)(?:st|nd|rd|th) District )?(Representative in Congress|U\.S\. Senate|Governor / Lt\. Governor)\b',l)
    if m: race=('house',m.group(1)) if m.group(1) else (('senate',None) if 'Senate' in l else ('governor',None)); off.setdefault(race,[]);i+=1;continue
    if race and re.search(r'\d+ (Year|Years) Term',l) and not m: race=None
    if race and PARTY.search(l) and i+2<len(L) and re.match(r'\d\d/\d\d/\d{4}',L[i+2]):
        off[race].append((l,L[i+1]));i+=2;continue
    i+=1
r=json.load(open('data/elections/MI/roster.json',encoding='utf-8'))
def n(s): return re.sub(r'[^a-z]','',unicodedata.normalize('NFKD',s).lower())
def key(name): return n(name.split()[-1])
PM={'DEM':'Democratic Party','REP':'Republican Party','GRN':'Green Party','LIB':'Libertarian Party','UST':'U.S. Taxpayers Party','NLP':'Natural Law Party','WCP':'Working Class Party','NPA':'No Party Affiliation'}
def rows(k):
    if k[0]=='house': return r['house'][k[1]]
    return r[k[0]]
tot=0
for k,v in off.items():
    ro=rows(k)
    offl={(p,n(nm.split(',')[0])) for p,nm in v}
    rl={(PM[c['party_code']],key(c['name'])) for c in ro if not c.get('write_in') and c['party_code']!='NPA' or (c['party_code']=='NPA' and not c.get('write_in'))}
    tot+=len(v)
    if offl!=rl: print(k,'official-only',sorted(offl-rl),'roster-only',sorted(rl-offl))
print('official rows',tot,{k:len(v) for k,v in off.items() if k[0]!='house'})
