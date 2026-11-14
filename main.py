import os, math, random, struct, zlib

W = H = 1024
RNG = random.Random(20261114)
pix = bytearray(W * H * 3)

def put(x, y, c, a=1.0):
    if x < 0 or y < 0 or x >= W or y >= H or a <= 0: return
    i = (int(y)*W + int(x))*3
    if a >= 0.999:
        pix[i:i+3] = bytes((int(c[0]), int(c[1]), int(c[2])))
    else:
        ia = 1-a
        pix[i] = int(pix[i]*ia + c[0]*a); pix[i+1] = int(pix[i+1]*ia + c[1]*a); pix[i+2] = int(pix[i+2]*ia + c[2]*a)

def ellipse(cx, cy, rx, ry, c, a=1.0, feather=1.5):
    x0=max(0,int(cx-rx-feather-1)); x1=min(W-1,int(cx+rx+feather+1)); y0=max(0,int(cy-ry-feather-1)); y1=min(H-1,int(cy+ry+feather+1))
    for y in range(y0,y1+1):
        dy=(y+.5-cy)/ry
        for x in range(x0,x1+1):
            d=math.sqrt(((x+.5-cx)/rx)**2+dy*dy)
            if d < 1+feather/max(rx,ry): put(x,y,c,a*min(1,(1-d)*max(rx,ry)/feather))

def radial_ellipse(cx,cy,rx,ry,inner,outer, feather=1.5):
    x0=max(0,int(cx-rx-feather)); x1=min(W-1,int(cx+rx+feather)); y0=max(0,int(cy-ry-feather)); y1=min(H-1,int(cy+ry+feather))
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            d=math.sqrt(((x+.5-cx)/rx)**2+((y+.5-cy)/ry)**2)
            if d < 1+feather/max(rx,ry):
                t=min(1,d); col=tuple(inner[k]*(1-t)+outer[k]*t for k in range(3))
                put(x,y,col,min(1,(1-d)*max(rx,ry)/feather))

def line(x1,y1,x2,y2,width,c,a=1.0):
    # rounded, antialiased capsule
    r=width/2; x0=max(0,int(min(x1,x2)-r-2)); x9=min(W-1,int(max(x1,x2)+r+2)); y0=max(0,int(min(y1,y2)-r-2)); y9=min(H-1,int(max(y1,y2)+r+2))
    dx=x2-x1; dy=y2-y1; den=dx*dx+dy*dy or 1
    for y in range(y0,y9+1):
        for x in range(x0,x9+1):
            t=max(0,min(1,((x+.5-x1)*dx+(y+.5-y1)*dy)/den)); xx=x1+t*dx; yy=y1+t*dy
            d=math.hypot(x+.5-xx,y+.5-yy)
            if d < r+1: put(x,y,c,a*min(1,r+1-d))

def bezier(points,width,c,a=1.0):
    last=None
    for n in range(45):
        t=n/44; u=1-t
        x=u**3*points[0][0]+3*u*u*t*points[1][0]+3*u*t*t*points[2][0]+t**3*points[3][0]
        y=u**3*points[0][1]+3*u*u*t*points[1][1]+3*u*t*t*points[2][1]+t**3*points[3][1]
        if last: line(last[0],last[1],x,y,width,c,a)
        last=(x,y)

def poly(pts,c,a=1):
    ys=range(max(0,int(min(p[1] for p in pts))),min(H-1,int(max(p[1] for p in pts)))+1)
    for y in ys:
        xs=[]
        for p,q in zip(pts,pts[1:]+pts[:1]):
            if (p[1]<=y+.5<q[1]) or (q[1]<=y+.5<p[1]): xs.append(p[0]+(y+.5-p[1])*(q[0]-p[0])/(q[1]-p[1]))
        xs.sort()
        for l,r in zip(xs[::2],xs[1::2]):
            for x in range(max(0,int(l)),min(W-1,int(r))+1): put(x,y,c,a)

def scene():
    # warm walnut table, broad plank bands and vignette
    for y in range(H):
        for x in range(W):
            d=math.hypot((x-512)/690,(y-490)/650)
            grain=5*math.sin(x*.025+math.sin(y*.013)*3)+3*math.sin(x*.09+y*.006)
            plank=7 if (y//180)%2 else 0
            v=max(0,1-d*.68)
            glow=max(0,1-d*1.12)
            put(x,y,(38*v+13*glow+grain+plank,20*v+6*glow+grain*.48+plank*.35,12*v+2*glow+grain*.18),1)
    for yy in (175,356,540,720,900): line(0,yy,W,yy,3,(20,10,8),.45)
    # bowl grounding shadows, then ceramic
    ellipse(520,727,423,258,(4,2,2),.62,28)
    radial_ellipse(512,555,425,358,(27,43,82),(8,16,42),3)
    ellipse(512,520,407,316,(81,120,169),1,2)
    ellipse(512,519,395,302,(15,31,75),1,2)
    ellipse(512,508,373,278,(117,155,192),1,2)
    radial_ellipse(512,500,355,260,(255,222,144),(145,76,31),2)
    # dark inner rim to give bowl depth
    ellipse(512,506,360,264,(35,45,62),.36,2)
    radial_ellipse(512,497,344,248,(248,204,116),(154,80,29),2)
    # oil pools
    for x,y,rx,ry in [(360,448,58,15),(621,470,63,18),(455,615,70,13),(673,560,40,12)]: ellipse(x,y,rx,ry,(202,91,24),.25,3)
    # nori behind food
    poly([(300,342),(390,371),(365,509),(274,476)],(13,27,28)); poly([(626,336),(713,315),(739,460),(650,483)],(11,25,26))
    poly([(311,351),(323,354),(294,468),(283,465)],(75,106,85),.22); poly([(641,347),(652,343),(680,462),(670,466)],(81,111,87),.22)
    # raised, generous noodle mattress: dense concentric sweeps keep broth as accents
    ellipse(512,526,244,143,(75,43,18),.30,18)
    for j in range(58):
        ang=j*math.pi*2/58; r=52+j*4.35
        x1=512+math.cos(ang)*r; y1=520+math.sin(ang)*r*.54
        x2=512+math.cos(ang+1.85)*r*.75; y2=510+math.sin(ang+1.85)*r*.42
        bezier([(x1+4,y1+9),(x1-80*math.sin(ang),y1+43),(x2+70*math.sin(ang),y2-32),(x2+4,y2+9)],11,(91,51,18),.49)
    for j in range(58):
        ang=j*math.pi*2/58+.12; r=52+j*4.35
        x1=512+math.cos(ang)*r; y1=510+math.sin(ang)*r*.54
        x2=512+math.cos(ang+1.85)*r*.75; y2=500+math.sin(ang+1.85)*r*.42
        col=((255,220,126),(239,177,65),(199,122,37),(255,235,153))[j%4]
        bezier([(x1,y1),(x1-80*math.sin(ang),y1+40),(x2+70*math.sin(ang),y2-35),(x2,y2)],7.5,col,.97)
    # the high central tangle catches the light, establishing a mound rather than a flat spiral
    for j in range(15):
        x=430+j*12; y=477+(j%3)*12
        bezier([(x,y),(x+14,431-j%4*7),(570+j*5,445+j%5*8),(598-j*4,501+j%4*8)],8,(255,218,120) if j%2 else (220,151,48),.96)
    # toppings currently basic: pork, eggs, naruto
    for cx,cy in [(365,575),(665,550)]:
        ellipse(cx+7,cy+11,94,64,(61,35,22),.35,5); ellipse(cx,cy,91,61,(108,54,30)); ellipse(cx,cy,82,54,(202,132,93))
        ellipse(cx-10,cy-5,54,29,(238,171,126),.38); ellipse(cx+23,cy+9,44,18,(133,65,44),.42)
        for rr in (22,36,49): ellipse(cx,cy,rr,rr*.57,(126,63,43),.16,2)
        for j in range(4):
            yy=cy-22+j*15
            bezier([(cx-52,yy),(cx-22,yy-9),(cx+18,yy+10),(cx+56,yy+3)],3,(91,42,25),.36)
    for cx,cy in [(445,403),(580,650)]:
        ellipse(cx+5,cy+10,73,54,(51,33,20),.34,4); ellipse(cx,cy,69,51,(247,238,211)); ellipse(cx+4,cy+1,35,33,(224,105,14)); ellipse(cx-7,cy-10,17,12,(255,201,65),.95,3); ellipse(cx+11,cy+10,15,10,(126,46,9),.3,2); ellipse(cx-1,cy-9,18,8,(255,243,166),.62,4)
    for cx,cy in [(686,414),(286,513)]:
        ellipse(cx,cy,38,30,(250,239,215)); ellipse(cx,cy,24,18,(238,137,154),.9)
        # spiral suggestion
        bezier([(cx+20,cy),(cx+18,cy-18),(cx-20,cy-20),(cx-15,cy+2)],4,(223,75,113)); bezier([(cx-15,cy+2),(cx-9,cy+15),(cx+12,cy+12),(cx+8,cy-1)],4,(223,75,113))
    # Improvement pass: broth sparkle, chili lacquer, and a crisp scallion mound
    ellipse(488,454,110,24,(255,248,210),.28,10)
    ellipse(548,470,65,12,(255,255,235),.24,7)
    ellipse(738,520,37,9,(255,235,174),.32,5)
    ellipse(305,555,35,11,(255,236,176),.25,6)
    for x,y,rx,ry in [(334,430,34,9),(715,457,47,12),(425,653,38,9),(675,615,28,8)]:
        ellipse(x,y,rx,ry,(218,115,31),.30,4)
        ellipse(x-rx*.18,y-ry*.24,rx*.38,ry*.22,(255,207,98),.32,3)
    for j in range(52):
        ang=RNG.random()*math.tau; rr=RNG.uniform(250,330)
        x=512+math.cos(ang)*rr; y=498+math.sin(ang)*rr*.66
        ellipse(x,y,RNG.uniform(1.3,3.2),RNG.uniform(1.0,2.3),(255,232,177),RNG.uniform(.30,.68),1)
    # red-orange aromatic oil: broken glossy curve at the exposed broth edge
    bezier([(286,610),(360,657),(465,677),(530,645)],5,(180,54,16),.65)
    bezier([(548,643),(611,615),(674,611),(724,638)],4,(193,59,15),.60)
    for x,y,r in [(322,625,7),(535,649,6),(699,630,8),(729,646,4),(248,475,5)]:
        ellipse(x,y,r,r*.62,(220,76,18),.85,2); ellipse(x-r*.25,y-r*.23,r*.25,r*.16,(255,193,89),.8,1)
    # scallion rings, clustered at the right side for a fresh green counterpoint
    for j in range(58):
        a=RNG.random()*math.tau; rr=math.sqrt(RNG.random())*62
        x=733+math.cos(a)*rr; y=536+math.sin(a)*rr*.54
        rx=RNG.uniform(5,10); ry=RNG.uniform(3,6)
        ellipse(x+2,y+3,rx,ry,(37,64,24),.35,2)
        ellipse(x,y,rx,ry,((42,112,45),(72,150,52),(115,177,65))[j%3],.96,1)
        ellipse(x,y,rx*.42,ry*.42,(205,193,98),.60,1)
    # sesame scattered on the pork, kept small enough to feel toasted rather than noisy
    for cx,cy in [(365,575),(665,550)]:
        for j in range(18):
            a=RNG.random()*math.tau; rr=math.sqrt(RNG.random())*55
            x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.55
            ellipse(x+1,y+2,2.7,1.4,(70,38,23),.35,1)
            ellipse(x,y,2.5,1.25,(250,220,143),.92,1)
    # fine steam, built from translucent overlapping puffs for a soft wisp edge
    for base, phase in [(410,0.1),(524,1.7),(645,3.2),(715,4.5)]:
        for k in range(8):
            y=365-k*22; x=base+math.sin(k*.8+phase)*15+k*1.1
            ellipse(x,y,14-k*.7,27-k*1.4,(255,245,221),.082,12)
    # porcelain and yolk pinpoints catch the upper-left warm key light
    ellipse(208,447,45,12,(145,188,222),.20,8)
    ellipse(431,390,13,8,(255,255,239),.72,3)
    ellipse(566,636,12,7,(255,237,158),.60,3)

scene()

def png(path):
    raw=b''.join(b'\0'+bytes(pix[y*W*3:(y+1)*W*3]) for y in range(H))
    def chunk(tag,data): return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    with open(path,'wb') as f:f.write(data)

out=os.environ.get('MAKEFUN_OUTPUT_DIR','/output'); os.makedirs(out,exist_ok=True); png(os.path.join(out,'entry.png'))
