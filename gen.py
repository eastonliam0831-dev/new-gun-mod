"""Generates 48 built-in resource packs, each with a 3D (cuboid) bow-replacement model.
Run:  python3 gen.py      Tweak HAND_* constants below if a gun sits wrong in your hand."""
import os, json, zlib, struct, re

OUT = "src/main/resources"
PACK_FORMAT = 97
HAND_SCALE_3P, HAND_SCALE_1P = 0.7, 0.8
HAND_BASE_3P = (0.0, 3.0, 1.0)      # base hand translation (x,y,z), before grip compensation
HAND_BASE_1P = (1.1, 3.0, -1.0)
HAND_ROT = (0, 90, 0)               # barrel forward. If the muzzle points at YOU use (0,-90,0).

GUNS = [
("SIG Sauer P365","compact","black"),("Colt M1911","pistol","steel"),("Glock 17","pistol","black"),
("Glock 43X","compact","black"),("SIG Sauer P320","pistol","black"),("Springfield Armory Hellcat Pro","compact","black"),
("Taurus TX22","pistol","black"),("Ruger Standard Mark IV","target","black"),("Smith and Wesson MP9 Shield","compact","black"),
("Walther PP PPK","compact","steel"),("Beretta 92FS M9","pistol","steel"),("SIG Sauer P226","pistol","steel"),
("CZ 75 Shadow 2","pistol","steel"),("Ruger LCP Max","tiny","black"),("PSA Dagger","pistol","black"),
("Luger Parabellum","luger","steel"),("Smith and Wesson Model 10","revolver","steel"),("Smith and Wesson J-Frame 642","snub","steel"),
("Colt Python","revolver","steel"),("Ruger Blackhawk","saa","black"),("Ruger LCR","snub","black"),
("Smith and Wesson Model 29","revolver","steel"),("Colt Single Action Army","saa","steel"),("Nagant M1895","revolver","blued"),
("AK-47 AKM","ak","wood"),("AR-15 M16 M4 Carbine","ar","black"),("Ruger 10-22","rifle","wood"),
("M1 Garand","garand","wood"),("M1 Carbine","carbine","wood"),("SKS","sks","wood"),
("Ruger PC Carbine","pcc","black"),("Mauser Model 98","bolt","wood"),("Mosin-Nagant M1891","bolt","wood"),
("Remington Model 700","scoped","wood"),("Winchester Model 94","lever","wood"),("Tikka T3x","scoped","black"),
("Ruger American Rifle","scoped","black"),("Winchester Model 70","scoped","wood"),("Lee-Enfield","bolt","wood"),
("Springfield M1903","bolt","wood"),("Savage Model 110","scoped","black"),("Marlin Model 1895 336","lever","wood"),
("Remington Model 870","pump","wood"),("Mossberg 500 590","pump","black"),("Mossberg Maverick 88","pump","black"),
("Browning Auto-5","auto_sg","wood"),("Benelli Super Black Eagle","auto_sg","black"),("Beretta A300 Ultima","auto_sg","black"),
]

# palette slots
PAL = [(26,26,30),(58,58,64),(150,155,165),(60,72,100),(135,90,50),(92,58,30),(42,42,46),(190,160,60),(200,205,215),(190,50,40),(255,255,255)]
BLK,DGR,STL,BLU,WOOD,DWOOD,GRIPC,BRASS,LSTL,RED,ACC = range(11)
FIN = {  # metal, dark, grip, wood/stock
 "black":(DGR,BLK,GRIPC,GRIPC),"steel":(STL,DGR,DWOOD,DWOOD),"blued":(BLU,BLK,DWOOD,DWOOD),"wood":(DGR,BLK,WOOD,WOOD)}

class G:
    def __init__(s,fin): s.e=[]; s.M,s.D,s.G,s.W=FIN[fin]
    def b(s,x0,y0,x1,y1,t,c,zc=0): s.e.append((x0,y0,x1,y1,zc-t,zc+t,c))

def pistol(g,L,gh,t=.6,toggle=False,thinbar=False):
    g.b(1,gh,1+L,gh+2.2,t,g.M); g.b(1.2,gh-1,L,gh,t-.1,g.D)
    g.b(1+L,gh+.6,1+L+.7,gh+1.6,.35,g.D)
    g.b(1,gh+2.2,1.6,gh+2.6,.25,g.D); g.b(L+.3,gh+2.2,L+1,gh+2.6,.25,g.D)
    g.b(1,gh/2,3.8,gh,.75,g.G); g.b(.5,0,3.4,gh/2,.75,g.G); g.b(.3,-.5,3.4,0,.8,g.D)
    g.b(3.9,gh-2,4.4,gh,.35,g.D); g.b(3.9,gh-2,6.6,gh-1.5,.35,g.D); g.b(6.2,gh-2,6.6,gh-1,.35,g.D)
    g.b(4.5,gh-1.4,4.8,gh-.1,.2,LSTL)
    g.b(2.4,gh+.5,3.0,gh+1.7,t+.02,ACC)
    if toggle: g.b(2.5,gh+2.2,4.8,gh+3.2,.4,g.M)
    return (2,gh/2)

def revolver(g,bl,gh,saa=False,lug=True):
    g.b(1,gh,6.4,gh+2.4,.55,g.M)
    g.b(3.6,gh-.3,6.2,gh+2.7,1.0,g.M); g.b(4.4,gh,5.4,gh+2.5,1.04,g.D)
    g.b(6.4,gh+.9,6.4+bl,gh+2.3,.5,g.M)
    if saa: g.b(6.4,gh+.2,6.4+bl*.8,gh+.6,.2,g.D)
    elif lug and bl>3: g.b(6.4,gh+.2,6.4+bl*.8,gh+.9,.45,g.D)
    g.b(6.4+bl-.5,gh+2.3,6.4+bl,gh+2.8,.2,g.D)
    g.b(.6,gh+2.4,1.6,gh+3.4,.3,g.D)
    g.b(3.4,gh-1.3,4.2,gh,.3,g.D); g.b(3.4,gh-1.3,5.6,gh-.8,.3,g.D)
    g.b(.8,gh-4,3.2,gh,.75,g.G); g.b(.4,gh-4.6,3.6,gh-3.6,.8,g.G)
    g.b(1.4,gh+.3,2.0,gh+1.5,.57,ACC)
    return (2,gh-2)

def longgun(g,kind):
    M,D,G,W=g.M,g.D,g.G,g.W
    end={"carbine":13,"pcc":13,"sks":16.5,"garand":16.5,"ar":16}.get(kind,16)
    # stock
    g.b(0,1.2,.5,5,.55,D); g.b(.5,3.2,5.5,5.2,.55,W); g.b(.5,1.5,2.8,3.2,.55,W)
    pg = kind in("ak","ar","pcc")
    if pg: g.b(5,.8,6.4,3.4,.5,G); g.b(3.6,3.0,5.5,4.2,.5,W if kind=="ak" else D)
    else:  g.b(3.5,2.2,6.2,4.4,.5,W)
    g.b(5.5,3.6,9.8,5.8,.6,M)
    g.b(9.8,4.3,end,5.1,.35,M)
    g.b(end-.6,5.1,end,5.7,.2,D); g.b(8.6,5.8,9.4,6.3,.2,D)
    hg={"ak":(9.8,3.7,13.5,W),"ar":(9.8,3.6,13.5,D),"rifle":(9.8,3.6,13,W),"carbine":(9.8,3.6,12,W),
        "sks":(9.8,3.6,15,W),"garand":(9.8,3.6,15.5,W),"pcc":(9.8,3.6,12.5,D),"bolt":(9.8,3.6,13.5,W),
        "scoped":(9.8,3.6,12.5,W),"lever":(9.8,3.6,13,W)}[kind]
    g.b(hg[0],hg[1],hg[2],5.4,.7,hg[3])
    if kind=="ak":
        g.b(9.8,5.4,13.5,5.9,.3,M); g.b(7.3,.6,8.5,3.6,.5,D); g.b(7.8,-.5,9.0,.6,.5,D)
    if kind=="ar":
        g.b(5.5,5.8,9.8,6.6,.35,M); g.b(7,.5,8.4,3.6,.5,D); g.b(end-.4,4.2,end+.4,5.2,.3,D)
    if kind in("sks","pcc","carbine","rifle"):
        g.b(7,1.5,8.2,3.6,.45,D)
    if kind=="garand": g.b(5.5,5.8,9.8,6.0,.4,D)
    if kind=="bolt": g.b(6.5,5.2,7,5.7,.2,M); g.b(7,5.0,7.6,5.6,.2,M,1.2); g.b(7.4,5.0,8.0,5.5,.4,DGR,1.5)
    if kind=="scoped":
        g.b(5.8,6.1,11.2,7.3,.65,BLK); g.b(5.8,5.8,6.3,6.1,.3,D); g.b(10.7,5.8,11.2,6.1,.3,D)
        g.b(5.6,6.5,5.8,6.9,.7,D); g.b(11.2,6.4,11.6,7.0,.85,D); g.b(7.5,5.0,8,5.4,.25,M,1.0)
    if kind=="lever":
        g.b(5.8,1.8,9.4,2.3,.2,M); g.b(5.8,1.8,6.3,3.6,.2,M); g.b(9.0,1.8,9.4,3.6,.2,M)
        g.b(9.8,3.2,13.5,3.6,.45,M)
    g.b(5.8,4.0,6.9,5.4,.62,ACC)
    return (5.7,2.4)

def shotgun(g,kind):
    M,D,G,W=g.M,g.D,g.G,g.W
    g.b(0,1.2,.5,5,.55,D); g.b(.5,3.0,5,5,.55,W); g.b(.5,1.5,3,3.0,.55,W)
    g.b(3.8,2.2,5.8,4.4,.5,W)
    g.b(5,3.4,9,5.6,.6,M); g.b(5.5,2.2,8.2,3.4,.5,D)
    g.b(9,4.3,16.5,5.3,.4,M); g.b(9,3.3,15,4.3,.38,D)
    g.b(16.0,5.3,16.5,5.8,.2,BRASS)
    if kind=="pump": g.b(9.6,2.8,13.2,4.3,.9,W); g.b(9.6,2.6,13.2,2.8,.5,D)
    else:
        g.b(9,3.0,12,4.3,.55,W); g.b(5.3,5.6,8.2,6.6,.55,M)  # humpback / vent rib hint
        g.b(9,5.3,16.5,5.6,.25,LSTL)
    g.b(5.8,4.2,7,5.4,.62,ACC)
    return (5,2.6)

def build(shape,fin):
    g=G(fin)
    if shape in("pistol","compact","tiny","target","luger"):
        L,gh={"pistol":(9,5),"compact":(7,4),"tiny":(5.5,3),"target":(9.5,5),"luger":(8.5,6)}[shape]
        t=.5 if shape=="tiny" else .6
        a=pistol(g,L,gh,t,toggle=shape=="luger")
        if shape=="target": g.b(1+L+.7,gh+.7,1+L+3,gh+1.5,.3,g.D)
    elif shape in("revolver","snub","saa"):
        bl,gh={"revolver":(5,5),"snub":(2,4),"saa":(5.5,5)}[shape]
        a=revolver(g,bl,gh,saa=shape=="saa",lug=shape=="revolver")
    elif shape in("pump","auto_sg"): a=shotgun(g,shape)
    else: a=longgun(g,shape)
    xs=[e[0] for e in g.e]+[e[2] for e in g.e]; ys=[e[1] for e in g.e]+[e[3] for e in g.e]
    zs=[e[4] for e in g.e]+[e[5] for e in g.e]
    cx,cy,cz=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2
    els=[]
    for x0,y0,x1,y1,z0,z1,c in g.e:
        uv=[c+.25,.25,c+.75,.75]
        f={k:{"uv":uv,"texture":"#0"} for k in("north","south","east","west","up","down")}
        els.append({"from":[round(x0-cx+8,3),round(y0-cy+8,3),round(z0-cz+8,3)],
                    "to":[round(x1-cx+8,3),round(y1-cy+8,3),round(z1-cz+8,3)],"faces":f})
    w,h=max(xs)-min(xs),max(ys)-min(ys)
    return els,(a[0]-cx,a[1]-cy),max(w,h)

def display(grip,size):
    gs=min(1.5,15/size)
    def hand(s,base):
        rx,ry,rz=HAND_ROT; gx,gy=grip
        return {"rotation":[rx,ry,rz],"scale":[s]*3,
                "translation":[round(base[0],2),round(base[1]-gy*s,2),round(base[2]+gx*s,2)]}
    def left(d): d=json.loads(json.dumps(d)); d["rotation"]=[d["rotation"][0],-d["rotation"][1],-d["rotation"][2]]; return d
    t3,t1=hand(HAND_SCALE_3P,HAND_BASE_3P),hand(HAND_SCALE_1P,HAND_BASE_1P)
    return {"thirdperson_righthand":t3,"thirdperson_lefthand":left(t3),
            "firstperson_righthand":t1,"firstperson_lefthand":left(t1),
            "gui":{"rotation":[20,-35,0],"translation":[0,0,0],"scale":[round(gs,2)]*3},
            "ground":{"rotation":[0,0,0],"translation":[0,2,0],"scale":[.5,.5,.5]},
            "fixed":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[round(gs*.9,2)]*3},
            "head":{"rotation":[0,180,0],"translation":[0,13,7],"scale":[1,1,1]}}

def png(px,path,w=16,h=16):
    raw=b"".join(b"\x00"+b"".join(bytes(p)+b"\xff" if p else b"\0\0\0\0" for p in row) for row in px)
    def ch(t,d):
        x=t+d; return struct.pack(">I",len(d))+x+struct.pack(">I",zlib.crc32(x)&0xffffffff)
    open(path,"wb").write(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b""))

names=[]
for i,(n,shape,fin) in enumerate(GUNS):
    slug=re.sub(r"[^a-z0-9]+","_",n.lower()).strip("_"); names.append((slug,n))
    base=f"{OUT}/resourcepacks/{slug}/assets/minecraft"
    for d in("items","models/item","textures/item"): os.makedirs(f"{base}/{d}",exist_ok=True)
    json.dump({"pack":{"description":f"Bow -> {n} (3D)","min_format":PACK_FORMAT,"max_format":PACK_FORMAT}},open(f"{OUT}/resourcepacks/{slug}/pack.mcmeta","w"))
    json.dump({"model":{"type":"minecraft:model","model":f"minecraft:item/gunbow_{slug}"}},open(f"{base}/items/bow.json","w"))
    els,grip,size=build(shape,fin)
    model={"textures":{"0":"minecraft:item/gunbow_palette","particle":"minecraft:item/gunbow_palette"},
           "gui_light":"side","elements":els,"display":display(grip,size)}
    json.dump(model,open(f"{base}/models/item/gunbow_{slug}.json","w"))
    pal=list(PAL); pal[ACC]=((i*37)%180+75,(i*91)%180+75,(i*53)%180+75)
    row=[pal[k] if k<len(pal) else None for k in range(16)]
    px=[[row[x] for x in range(16)] for _ in range(16)]
    png(px,f"{base}/textures/item/gunbow_palette.png")
json.dump(names,open(OUT+"/guns.json","w"),indent=1)
print(len(names),"3D packs")
