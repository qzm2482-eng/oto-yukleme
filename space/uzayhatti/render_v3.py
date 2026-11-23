"""Orbit Archives renderer v3 (derived from render_b.py). usage: render_v3.py out_video.mp4 [limit_seconds]"""
import json, subprocess, sys, os
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0,'/home/claude/space/ep02')
from script_data import FRAMES, HOOK
os.chdir('/home/claude/space/ep02')
W,H,FPS=1080,1920,30
F="/home/claude/oto-yukleme/assets/fonts/montserrat-latin-900.ttf"
AMBER=(245,166,35)
T=json.load(open('timing.json')); words=T['words']
TAIL=1.0; DUR=T['dur']+TAIL
OUT=sys.argv[1]; LIMIT=float(sys.argv[2]) if len(sys.argv)>2 else None
# ---- subtitle screens: (sentence,chunk) groups
scr={}
for w in words: scr.setdefault((w['sent'],w['chunk']),[]).append(w)
keys=sorted(scr); screens=[]
for n,k in enumerate(keys):
    ws=scr[k]; s=ws[0]['start']-0.04
    nxt=scr[keys[n+1]][0]['start']-0.04 if n+1<len(keys) else 1e9
    e=min(nxt, ws[-1]['end']+0.18)
    if n+1<len(keys) and nxt-ws[-1]['end']<0.5 : e=nxt
    screens.append(dict(key=k,start=max(0,s),end=e,words=[(x['d'].rstrip('.,;:!').replace('"',''),x['amber']) for x in ws]))
for sc in screens: assert len(sc['words'])<=5
# ---- frames
fstart=[scr[k][0]['start'] if k!=(0,0) else 0.0 for _,k in FRAMES]
shots=[(FRAMES[i][0],fstart[i],(fstart[i+1] if i+1<len(FRAMES) else DUR)) for i in range(len(FRAMES))]
json.dump(dict(shots=shots,screens=[dict(text=' '.join(w for w,_ in s['words']),start=s['start'],end=s['end']) for s in screens],dur=DUR),open('meta/timeline.json','w'),indent=1)
def prep(n):
    im=Image.open(f'img/{n}.jpg').convert('RGB'); im=ImageEnhance.Contrast(im).enhance(1.08)
    s=max(W/im.width,H/im.height); bg=im.resize((int(im.width*s)+2,int(im.height*s)+2)).crop((0,0,W,H)).filter(ImageFilter.GaussianBlur(40))
    bg=ImageEnhance.Brightness(bg).enhance(0.38)
    return im,np.asarray(bg)
P={n:prep(n) for n in {s[0] for s in shots}}
FS=lambda sz:ImageFont.truetype(F,sz)
grad=np.zeros((H,W,1),np.float32); yy=np.arange(H)[:,None,None]; grad=np.clip(1-yy/800,0,1)*0.6*np.ones((1,W,1),np.float32)
CY=1000; BW=W; MAXH=1500
def fg_of(name,a,b,t):
    im,bg=P[name]; p=min(max((t-a)/max(b-a,0.1),0),1); z=1.0+0.06*p
    bh=int(min(BW*im.height/im.width,MAXH)); cw=im.width/z; ch=cw*bh/BW
    x0=(im.width-cw)/2; y0=(im.height-ch)/2
    fg=im.transform((BW,bh),Image.AFFINE,(cw/BW,0,x0,0,ch/bh,y0),Image.BICUBIC)
    fr=bg.copy(); y=CY-bh//2; fr[y:y+bh,:,:]=np.asarray(fg); return fr.astype(np.float32)
def shotfr(t):
    i=max(k for k,s in enumerate(shots) if s[1]<=t); fr=fg_of(*shots[i],t)
    if i>0 and t-shots[i][1]<0.35:
        a=(t-shots[i][1])/0.35; fr=fr*a+fg_of(*shots[i-1],t)*(1-a)
    return fr
def lines(d,words,maxw=960):
    for sz in (100,92,84,76,68):
        f=FS(sz); ls=[[]]
        for w in words:
            cand=' '.join(x[0].upper() for x in ls[-1]+[w])
            if ls[-1] and d.textlength(cand,font=f)>maxw: ls.append([w])
            else: ls[-1].append(w)
        if len(ls)==2:
            allw=ls[0]+ls[1]; best=None
            for k in range(1,len(allw)):
                cand=[allw[:k],allw[k:]]; m=max(d.textlength(' '.join(x[0].upper() for x in l),font=f) for l in cand)
                if best is None or m<best[0]: best=(m,cand)
            ls=best[1]
        if len(ls)<=2 and all(d.textlength(' '.join(x[0].upper() for x in l),font=f)<=maxw for l in ls): return f,ls
    return f,ls
def draw_words(d,f,ls,y0,lh):
    for li,l in enumerate(ls):
        texts=[w[0].upper() for w in l]; sp=d.textlength(' ',font=f)+18; ws=[d.textlength(x,font=f) for x in texts]
        x=(W-sum(ws)-sp*(len(ws)-1))/2; y=y0+li*lh
        for (tx,am),wd in zip(zip(texts,[w[1] for w in l]),ws):
            d.text((x,y),tx,font=f,fill=AMBER if am else 'white',stroke_width=9,stroke_fill='black'); x+=wd+sp
LAB="SALYUT 1 · 1971"
def frame(t):
    fr=shotfr(t); fr=fr*(1-grad)
    im=Image.fromarray(np.clip(fr,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    if t<2.8:   # hook text (upper zone), fades out 2.5-2.8
        hf=FS(150); a=1.0 if t<2.5 else max(0,(2.8-t)/0.3)
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        for li,l in enumerate(HOOK):
            parts=l.split(); sp=ld.textlength(' ',font=hf)+22; ws=[ld.textlength(p,font=hf) for p in parts]; x=(W-sum(ws)-sp*(len(ws)-1))/2
            for p,wd in zip(parts,ws):
                ld.text((x,260+li*165),p,font=hf,fill=AMBER+(255,) if p=='23' else (255,255,255,255),stroke_width=11,stroke_fill=(0,0,0,255)); x+=wd+sp
        if a<1: lay.putalpha(lay.getchannel('A').point(lambda v:int(v*a)))
        im.paste(lay,(0,0),lay)
    cur=[s for s in screens if s['start']<=t<s['end']]
    if cur:
        s=cur[0]; f,ls=lines(d,s['words']); draw_words(d,f,ls,820,int(f.size*1.18))
    a=np.asarray(im).astype(np.int16)+NOISE[int(t*FPS)%8]
    return np.clip(a,0,255).astype(np.uint8).tobytes()
rng=np.random.default_rng(3); NOISE=[rng.normal(0,3,(H,W,1)).astype(np.int16) for _ in range(8)]
if __name__=='__main__':
    dur=LIMIT or DUR; n=int(dur*FPS)
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-t',str(dur),OUT],stdin=subprocess.PIPE)
    with Pool(2) as pool:
        for b in pool.imap(frame,[i/FPS for i in range(n)],chunksize=6): p.stdin.write(b)
    p.stdin.close(); p.wait(); print('ok',dur)
