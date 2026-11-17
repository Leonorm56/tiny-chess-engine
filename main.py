# Emberfall: a 4 KB Python chess engine for the tiny-chess-01 gauntlet (MIT).
import base64,json,os,urllib.request
U=os.environ["MAKEFUN_ENV_URL"]
V=(1,3,3,5,9,0)
M=(100,320,330,500,900,0)
T=base64.b64decode("AAAAAAAAAAA8PDw8PDw8PA8PGSMjGQ8PBQUMHh4MBQUAAAAWFgAAAAT4+AAA+PgEBAgI7u4ICAQAAAAAAAAAAMnd5+zs593J3fEAAAAA8d3nAAwSEgwA5+wFEhkZEgXs7AASGRkSAOznBQwSEgwF593xAAUFAPHdyd3n7Ozn3cns9vb29vb27PYFAAAAAAX29goKDg4KCvb2BQ4SEg4F9vYADhISDgD29ggKDg4KCPb2CgIAAAIK9uz22Pb22PbsAAAAAgIAAAAIDAwMDAwMCPwAAAAAAAD8/AAAAAAAAPz8AAAAAAAA/PwAAAAAAAD8/AAAAAAAAPwAAAIGBgIAAOz29vv79vbs9gACAAACAPb2AgYGBgYC9vsABggIBgD7AAAGCAgGAPv2BAYGBgYC9vYABAAAAgD27Pb2+/v29uzOxMS6usTEzs7ExLq6xMTOzsTEurrExM7OxMS6usTEztjOzsTEzs7Y7OLi2Nji4uwUFPbs7PYUFBkjCgAACiMZ")
D={2:(33,31,18,14,-14,-18,-31,-33),3:(17,15,-15,-17),4:(16,1,-1,-16),5:(17,15,-15,-17,16,1,-1,-16),6:(17,15,-15,-17,16,1,-1,-16)}
W=[0]*2048
for i in range(128):
 if not i&136:
  r,y=i>>4,i&7
  for t in range(1,7):
   a=T[(t-1)*64+r*8+y];a-=256*(a>127)
   z=T[(t-1)*64+(7-r)*8+y];z-=256*(z>127)
   W[t*128+i]=a+M[t-1]
   W[(t+8)*128+i]=-z-M[t-1]


N=[0,0]
LIM=150000
K=[]

def post(p,j):
 r=urllib.request.Request(U+p,json.dumps(j).encode(),{"content-type":"application/json"})
 return json.load(urllib.request.urlopen(r))


def bd(f):
 b=[0]*128
 r=c=0
 for ch in f.split()[0]:
  if ch=="/":
   r+=1;c=0
  elif ch>"8":
   b[r*16+c]=" PNBRQK".index(ch.upper())+(8 if ch>"Z" else 0);c+=1
  else:
   c+=int(ch)
 return b


def KV(b,m):
 v=b[m&127]
 return (V[(v&7)-1]*9 if v else 0)+(m>>14)


def mv(b,w,o=0):
 C=[];Q=[]
 g=0 if w else 8
 for i in range(128):
  p=b[i]
  if not p or p&8!=g:
   continue
  t=p&7
  if t==1:
   d=-16 if not g else 16
   j=i+d
   if not j&136 and not b[j]:
    if j>>4 in (0,7):
     C+=[i<<7|j|x<<14 for x in (5,2)]
    else:
     Q.append(i<<7|j)
     if i>>4 in (1,6) and not b[j+d]:
      Q.append(i<<7|j+d)
   for j in (i+d-1,i+d+1):
    if not j&136 and b[j] and b[j]&8!=g:
     if j>>4 in (0,7):
      C+=[i<<7|j|x<<14 for x in (5,2)]
     else:
      C.append(i<<7|j)
  else:
   for o2 in D[t]:
    j=i
    while 1:
     j+=o2
     if j&136:
      break
     v=b[j]
     if v:
      if v&8!=g:
       C.append(i<<7|j)
      break
     if not o:
      Q.append(i<<7|j)
     if t==2 or t==6:
      break
 C.sort(key=lambda m:-KV(b,m))
 return C if o else C+Q


def mk(b,m):
 f=m>>7&127;t=m&127
 c=b[t];b[t]=b[f];b[f]=0
 if m>>14:
  b[t]=m>>14|(b[t]&8)
 return c


def un(b,m,c):
 f=m>>7&127;t=m&127
 b[f]=1|(b[t]&8) if m>>14 else b[t]
 b[t]=c


def ev(b,w):
 return sum(W[p*128+i] for i,p in enumerate(b))*(1 if w else -1)


def qs(b,a,z,w,d=0):
 N[0]+=1
 if N[0]>LIM:
  N[1]=1
  return ev(b,w)
 s=ev(b,w)
 if s>=z:
  return s
 if s>a:
  a=s
 if d>2:
  return a
 for m in mv(b,w,1):
  v=b[m&127]
  f=m>>7&127
  if v:
   at=V[(b[f]&7)-1]
   vt=V[(v&7)-1]
   if at>vt:
    continue
   if s+vt*100+150<a:
    continue
  c=mk(b,m)
  if c&7==6:
   un(b,m,c)
   return 9999-d
  s=-qs(b,-z,-a,w^1,d+1)
  un(b,m,c)
  if s>a:
   a=s
   if a>=z:
    break
 return a


def ab(b,d,a,z,w):
 N[0]+=1
 if N[0]>LIM:
  N[1]=1
  return ev(b,w)
 if d<1:
  return qs(b,a,z,w)
 best=-9999
 for m in mv(b,w):
  c=mk(b,m)
  if c&7==6:
   un(b,m,c)
   return 9999
  s=-ab(b,d-1,-z,-a,w^1)
  un(b,m,c)
  if s>best:
   best=s
  if s>a:
   a=s
   if a>=z:
    break
 return best


def sq(s):
 return (8-int(s[1]))*16+"abcdefgh".index(s[0])


def ui(u):
 return sq(u[:2])<<7|sq(u[2:4])|((("nbrq".index(u[4])+2)<<14) if len(u)>4 else 0)


def think(b,w,ms):
 best=ms[0]
 N[0]=N[1]=0
 ms=sorted(ms,key=lambda u:-KV(b,ui(u))-(ui(u) in K[-6:])*4)
 for d in range(1,5):
  bv=-9999;bb=ms[0];N[1]=0
  for u in ms:
   m=ui(u)
   c=mk(b,m)
   s=-ab(b,d-1,-9999,-bv,w^1)
   un(b,m,c)
   if s>bv:
    bv,bb=s,u
  if N[1]:
   break
  best=bb
  ms=[best]+[u for u in ms if u!=best]
 return best


while 1:
 g=post("/game",{})
 K[:]=[]
 if g["status"]=="done":
  print(g)
  break
 while g["status"]=="your_move":
  b=bd(g["fen"])
  m=think(b,g["colour"]=="white",g["legal_moves"])
  K.append(ui(m))
  g=post("/move",{"game":g["game"],"move":m})
