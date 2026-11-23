import json, subprocess, sys, re, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
F="/home/claude/oto-yukleme/assets/fonts/montserrat-latin-900.ttf"
D='/home/claude/space/apollo13/'
OUT=sys.argv[1]; LIMIT=float(sys.argv[2]) if len(sys.argv)>2 else None
words=json.load(open(D+'work/voice.mp3.json')); voice=D+'work/voice.mp3'
TAIL=1.2; dur=words[-1][1]+0.0+TAIL
# ---- shots (image, start) ; ends at dur
SH=[('AS13-62-8929',0),('AS13-59-8562',3.9),('AS13-59-8484',7.4),('AS13-59-8500',11.0),('AS13-62-8929',14.3),('S70-34904',17.5),
    ('S70-34902',20.9),('AS13-62-8929',24.2),('S70-35014',29.4),('AS13-60-8588',33.2),('AS13-59-8484',36.4)]
shots=[(n,a,(SH[i+1][1] if i+1<len(SH) else dur)) for i,(n,a) in enumerate(SH)]
json.dump(shots,open(D+'work/shots.json','w'))
ROT={'AS13-59-8484':-90}   # Lovell frame is stored sideways
BOXW,BOXH,BOXCY=960,840,1085
FONT=ImageFont.truetype(F,80)
STOP={'a','an','the','and','to','of','it','was','had','in','into','for','over','then','at','through','that','were','on'}
# ---- caption groups: manual hook, auto for rest
SIZES={1:[5,3,3,3],2:[5,4,4],3:[5,5,3],4:[4,3],5:[4,5,3],6:[4,4,3],7:[5,1,3,2],8:[5,4],9:[5],10:[3,3,4],11:[4,4],12:[5]}
def chunk(ws,si):
    out=[];i=0
    for sz in SIZES[si]: out.append(ws[i:i+sz]); i+=sz
    assert i==len(ws),(si,len(ws),i)
    return out
def wrap(txts):
    lines=[];cur=''
    for t in txts:
        c=(cur+' '+t).strip()
        if FONT.getlength(c.upper())>940 and cur: lines.append(cur);cur=t
        else: cur=c
    lines.append(cur); return lines
sents={}
for w in words: sents.setdefault(w[3],[]).append(w)
groups=[]
for si,ws in sents.items():
    ws=[[a,b,re.sub(r"[^\w']",'',t)] for a,b,t,_,_ in ws]
    if si==0: groups.append(dict(ws=ws,lines=['SQUARE FILTER','ROUND HOLE'],hi='HOLE',t0=0.0)); continue
    # balanced grouping: smallest number of groups
    for g in chunk(ws,si):
        groups.append(dict(ws=g,t0=g[0][0]))
for g in groups:
    if 'lines' not in g:
        txts=[w[2].upper() for w in g['ws']]
        cand=[w for w in txts if w.lower() not in STOP] or txts
        g['hi']=max(cand,key=len)
        # balanced wrap
        if FONT.getlength(' '.join(txts))>880 and len(txts)>=2:
            best=min(range(1,len(txts)),key=lambda k:max(FONT.getlength(' '.join(txts[:k])),FONT.getlength(' '.join(txts[k:]))))
            g['lines']=[' '.join(txts[:best]),' '.join(txts[best:])]
        else: g['lines']=[' '.join(txts)]
for i,g in enumerate(groups): g['t1']=groups[i+1]['t0'] if i+1<len(groups) else words[-1][1]+0.3
json.dump([dict(t0=g['t0'],t1=g['t1'],lines=g['lines'],hi=g['hi'],words=[w[2] for w in g['ws']]) for g in groups],open(D+'work/captions.json','w'),indent=1)
def cap_img(g):
    im=Image.new('RGBA',(W,320),(0,0,0,0)); d=ImageDraw.Draw(im); lh=104; n=len(g['lines']); y0=160-n*lh/2+lh/2
    hi_done=False
    for li,line in enumerate(g['lines']):
        ws=line.split(' '); sp=FONT.getlength(' '); tw=sum(FONT.getlength(w) for w in ws)+sp*(len(ws)-1); x=(W-tw)/2
        for w in ws:
            col=(245,166,35) if (w==g['hi'] and not hi_done) else (255,255,255)
            if col!=(255,255,255): hi_done=True
            d.text((x,y0+li*lh),w,font=FONT,fill=col,stroke_width=8,stroke_fill=(0,0,0),anchor='lm'); x+=FONT.getlength(w)+sp
    return im
CAPS=[cap_img(g) for g in groups]; CAPY=520-160
# ---- images
def prep(name):
    im=Image.open(D+f'img/{name}.jpg').convert('RGB')
    if name in ROT: im=im.rotate(ROT[name],expand=True)   # PIL: positive = counter-clockwise
    im=ImageEnhance.Contrast(im).enhance(1.06)
    s=min(BOXW/im.width,BOXH/im.height); bw,bh=int(im.width*s),int(im.height*s)
    big=im.resize((bw*2,bh*2),Image.LANCZOS)            # 2x oversample before zoom (no stair-step jitter)
    sc=max(W/im.width,H/im.height)
    bg=im.resize((int(im.width*sc)+2,int(im.height*sc)+2),Image.BILINEAR)
    x=(bg.width-W)//2; y=(bg.height-H)//2; bg=bg.crop((x,y,x+W,y+H)).filter(ImageFilter.GaussianBlur(40)); bg=ImageEnhance.Brightness(bg).enhance(0.40)
    m=Image.new('L',(bw,bh),0); ImageDraw.Draw(m).rounded_rectangle([0,0,bw-1,bh-1],34,fill=255)
    sh=Image.new('L',(W,H),0); px,py=(W-bw)//2,BOXCY-bh//2; ImageDraw.Draw(sh).rounded_rectangle([px+8,py+14,px+bw+8,py+bh+14],34,fill=170)
    bg.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(18)))
    return dict(big=big,bg=bg,bw=bw,bh=bh,m=m,px=px,py=py)
P={n:prep(n) for n in {s[0] for s in shots}}
def shot_img(name,a,b,t):
    p=P[name]; pr=min(max((t-a)/max(b-a,0.1),0),1); z=1.0+0.07*pr
    bw2,bh2=p['big'].size; cw,ch=bw2/z,bh2/z; x0=(bw2-cw)/2; y0=(bh2-ch)/2
    fg=p['big'].transform((p['bw'],p['bh']),Image.AFFINE,(cw/p['bw'],0,x0,0,ch/p['bh'],y0),Image.BICUBIC)
    fr=p['bg'].copy(); fr.paste(fg,(p['px'],p['py']),p['m']); return fr
def frame(t):
    i=max(k for k,s in enumerate(shots) if s[1]<=t); fr=shot_img(*shots[i],t)
    if i>0 and t-shots[i][1]<0.4: fr=Image.blend(shot_img(*shots[i-1],t),fr,(t-shots[i][1])/0.4)
    gi=[k for k,g in enumerate(groups) if g['t0']-0.0<=t<g['t1']]
    if gi: fr.paste(CAPS[gi[0]],(0,CAPY),CAPS[gi[0]])
    return fr
if LIMIT: dur_out=LIMIT
else: dur_out=dur
BV=0.1
af=('[2]tremolo=f=0.15:d=0.4,highpass=f=80,lowpass=f=1800[pad];[3]highpass=f=200,lowpass=f=3000[air];'
    f'[pad][air]amix=2:normalize=0,volume={BV},afade=t=in:d=0.8,afade=t=out:st={dur-1.4:.2f}:d=1.2[bed];'
    '[1]apad,asplit=2[v][sc];[bed][sc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[duck];'
    '[v][duck]amix=2:duration=first:normalize=0[mix]')
cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
 '-i',voice,'-f','lavfi','-i',f'aevalsrc=0.25*sin(2*PI*110*t)+0.18*sin(2*PI*164.8*t)+0.14*sin(2*PI*220*t)+0.08*sin(2*PI*329.6*t):d={dur}:s=44100',
 '-f','lavfi','-i',f'anoisesrc=c=pink:d={dur}:a=0.05','-filter_complex',af+';[mix]aresample=44100[a]',
 '-map','0:v','-map','[a]','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','pcm_s16le','-t',str(dur_out),OUT]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for i in range(int(dur_out*FPS)): p.stdin.write(frame(i/FPS).tobytes())
p.stdin.close(); p.wait(); print('ok',dur)
