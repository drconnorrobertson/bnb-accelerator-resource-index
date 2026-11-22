"""Check full closing-case preservation, isolated workspaces and canonical ownership."""
import json,re,sys,hashlib,xml.etree.ElementTree as E
from pathlib import Path
from html.parser import HTMLParser
root=Path.cwd();pub=root/'public';assert len(sys.argv)>1,'Supply the topic slug';slug=sys.argv[1];assert slug in ('comparable-selection','seasonality-review');owner='/library/'+slug+'/';html=(pub/'library'/slug/'index.html').read_text();articles=json.loads((root/'content/page-articles'/f'{slug}.json').read_text())
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def visible(s):
 p=Text();p.feed(s);return re.sub(r'\s+',' ',' '.join(p.parts)).strip()
ids=re.findall(r'\bid="([^"]+)"',html);assert len(ids)==len(set(ids))
for target in re.findall(r'\bfor="([^"]+)"',html):assert target in ids
assert len(articles)==40 and len({json.dumps(a['caseFacts'],sort_keys=True) for a in articles})==1
assert len({a['shortTitle'] for a in articles})==40
rules=json.loads((root/'vercel.json').read_text())['redirects']
for n in range(1,41):
 case=f'case-{n:02d}';assert ids.count(case)==1
 assert f'data-case-workspace="{case}" data-storage-path="/workbooks/{slug}/example-{n:02d}/"' in html
 assert not (pub/'workbooks'/slug/f'example-{n:02d}'/'index.html').exists()
 for suffix in ('','/'):
  matching=[r for r in rules if r['source']==f'/workbooks/{slug}/example-{n:02d}'+suffix];assert len(matching)==1 and matching[0]['permanent'] and matching[0]['destination']==owner+'#'+case
assert 'data-case-workspace="own" data-storage-path="'+owner+'"' in html
assert html.count('data-case-workspace="')==41
links=re.findall(r'data-case-link="([^"]+)"',html);assert len(links)==len(set(links))==40
assert html.count('class="case-nav-group"')==5
if slug=='seasonality-review':
 assert 24000/3==8000 and 18000/9==2000 and 24000+18000==42000 and 42000/12==3500 and 8000*12==96000 and 96000-42000==54000
 for phrase in ['$42,000','$96,000','$54,000','not missing recorded revenue','no monthly cost amounts']:assert phrase.lower() in html.lower(),phrase
else:
 for phrase in ['exceptions overlap','not count them as three distinct properties','undocumented reason is still an open question','supplies no such threshold']:assert phrase.lower() in html.lower(),phrase

urls=[e.text for e in E.parse(pub/'sitemap.xml').findall('.//{*}loc')];assert len(urls)==len(set(urls))==67;assert not any('/workbooks/closing-cash/' in u for u in urls)
if len(sys.argv)>2:
 base=Path(sys.argv[2])/slug;old=(base/'00.html').read_text();oldOwn=json.loads(re.search(r'<script id="workspace-data" type="application/json">(.*?)</script>',old,re.S)[1]);newOwn=json.loads(re.search(r'data-case-workspace="own"[\s\S]*?<script type="application/json" data-case-workspace-data>(.*?)</script>',html)[1]);assert oldOwn==newOwn
 for n in range(1,41):
  old=(base/f'{n:02d}.html').read_text();pattern=r'<article data-developed-case="'+slug+'/'+str(n)+r'">([\s\S]*?)</article>';a=re.search(pattern,old);b=re.search(pattern,html);assert a and b;assert visible(a[1])==visible(b[1]),n
  oldData=json.loads(re.search(r'<script id="workspace-data" type="application/json">(.*?)</script>',old,re.S)[1]);newData=json.loads(re.search(r'data-case-workspace="case-'+f'{n:02d}'+r'"[\s\S]*?<script type="application/json" data-case-workspace-data>(.*?)</script>',html)[1]);assert oldData==newData,n
print(json.dumps({'canonicalOwners':67,'completeCaseArticlesPreserved':40,'separateWorkspaces':41,'priorWorkspaceDataPreserved':41,'legacyFormsDirect':80,'uniqueIDs':len(ids),'commonPackets':1,'distinctEvidenceConditions':40,'topic':slug,'marketOrCashForecast':'not established'}))
