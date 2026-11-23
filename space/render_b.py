import json, subprocess, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=720,1280,30
F="/home/claude/oto-yukleme/assets/fonts/montserrat-latin-900.ttf"
BV=sys.argv[4] if len(sys.argv)>4 else '0.1'
voice=sys.argv[1]; words=json.load(open(voice+'.json')); label=sys.argv[3]
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',voice]))+0.6
import os
SH=json.load(open(sys.argv[5])) if len(sys.argv)>5 else [['dmg.jpg',0],['spektr.jpg',4.2]]
shots=[(n,a,(SH[i+1][1] if i+1<len(SH) else dur)) for i,(n,a) in enumerate(SH)]
groups=[];cur=[]
_f=ImageFont.truetype(F,58)
for k,w in enumerate(words):
    t=' '.join(words[j][2].upper() for j in cur+[k])
    if cur and (len(cur)>=3 or _f.getlength(t)>620 or w[2].endswith(',')): groups.append(cur);cur=[]
    cur.append(k)
    if w[2][-1] in '.,' or k==0: groups.append(cur);cur=[]
if cur: groups.append(cur)
gof={k:g for g in groups for k in g}
def prep(n):
    im=ImageEnhance.Contrast(Image.open(n).convert('RGB')).enhance(1.12)
    s=max(W/im.width,H/im.height); bg=im.resize((int(im.width*s)+2,int(im.height*s)+2)).crop((0,0,W,H)).filter(ImageFilter.GaussianBlur(28))
    bg=ImageEnhance.Brightness(bg).enhance(0.45)
    return im,bg
P={n:prep(n) for n,_,_ in shots}
fb=ImageFont.truetype(F,58); fl=ImageFont.truetype(F,34); rng=np.random.default_rng(1)
BOX_W=680; BOX_Y=250
def shot_img(name,a,b,t):
    im,bg=P[name]; p=(t-a)/max(b-a,0.1); z=1.0+0.08*p
    bh=int(BOX_W*min(im.height/im.width,0.9)); cw,ch=im.width/z,im.width/z*bh/BOX_W
    x0=(im.width-cw)/2; y0=max(0,min((im.height-ch)/2,im.height-ch))
    fg=im.transform((BOX_W,bh),Image.AFFINE,(cw/BOX_W,0,x0,0,ch/bh,y0),Image.BICUBIC)
    fr=bg.copy(); m=Image.new('L',(BOX_W,bh),0); ImageDraw.Draw(m).rounded_rectangle([0,0,BOX_W-1,bh-1],22,fill=255)
    sh=Image.new('L',(W,H),0); ImageDraw.Draw(sh).rounded_rectangle([(W-BOX_W)//2+6,BOX_Y+10,(W+BOX_W)//2+6,BOX_Y+bh+10],22,fill=160)
    fr.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(12))); fr.paste(fg,((W-BOX_W)//2,BOX_Y),m)
    return fr,bh
def frame(t):
    i=max(k for k,s in enumerate(shots) if s[1]<=t); fr,bh=shot_img(*shots[i],t)
    if i>0 and t-shots[i][1]<0.4: fr=Image.blend(shot_img(*shots[i-1],t)[0],fr,(t-shots[i][1])/0.4)
    d=ImageDraw.Draw(fr)
    tw=d.textlength(label,font=fl); d.rounded_rectangle([W/2-tw/2-22,150,W/2+tw/2+22,206],14,fill=(200,20,20)); d.text((W/2,178),label,font=fl,fill='white',anchor='mm')
    idx=max([k for k,w in enumerate(words) if w[0]<=t+0.05] or [0]); g=gof[idx]; g0=g[0]; grp=[words[k] for k in g]
    if t<words[-1][1]+0.4:
        texts=[w[2].upper() for w in grp]; sp=16; ws=[d.textlength(x,font=fb) for x in texts]; x=(W-sum(ws)-sp*(len(ws)-1))/2; y=895
        for k,(tx,wd) in enumerate(zip(texts,ws)):
            d.text((x,y),tx,font=fb,fill=(255,77,77) if g0+k==idx else 'white',stroke_width=6,stroke_fill='black'); x+=wd+sp
    a=np.asarray(fr).astype(np.float32)+rng.normal(0,4,(H,W,1)); return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
 '-i',voice,'-f','lavfi','-i',f'aevalsrc=0.25*sin(2*PI*110*t)+0.18*sin(2*PI*164.8*t)+0.14*sin(2*PI*220*t)+0.08*sin(2*PI*329.6*t):d={dur}:s=44100','-f','lavfi','-i',f'anoisesrc=c=pink:d={dur}:a=0.05',
 '-filter_complex','[2]tremolo=f=0.15:d=0.4,highpass=f=80,lowpass=f=1800[pad];[3]highpass=f=200,lowpass=f=3000[air];[pad][air]amix=2:normalize=0,volume='+BV+',afade=t=in:d=0.8,afade=t=out:st=%f:d=0.6[bed];[1]apad,asplit=2[v][sc];[bed][sc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[duck];[v][duck]amix=2:duration=first:normalize=0,loudnorm=I=-15:TP=-2.5[a]'%(dur-0.6),
 '-map','0:v','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(dur),sys.argv[2]],stdin=subprocess.PIPE)
for i in range(int(dur*FPS)): p.stdin.write(frame(i/FPS).tobytes())
p.stdin.close(); p.wait(); print('ok',dur)
