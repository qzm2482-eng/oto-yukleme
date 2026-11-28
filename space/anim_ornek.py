import numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W,H,F=540,960,24; T=7.0; N=int(T*F)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fb=lambda s:ImageFont.truetype(B,s)
rng=np.random.default_rng(1); P=1800
ang=rng.uniform(0,2*np.pi,P); spd=rng.uniform(30,300,P); up=rng.uniform(0,1,P)
vx=np.cos(ang)*spd; vy=np.sin(ang)*spd*0.6-up*260
cx,cy=W/2,H*0.62
def boom(t):
    img=np.zeros((H,W,3),np.float32)
    k=1-np.exp(-t*2.2)
    x=cx+vx*k*0.9; y=cy+vy*k*0.9-t*60*up
    life=np.clip(1-t/3.2,0,1)
    m=(x>0)&(x<W-1)&(y>0)&(y<H-1)
    xi,yi=x[m].astype(int),y[m].astype(int)
    heat=np.clip(1.3-spd[m]/300-t*0.2,0,1)
    col=np.stack([np.ones_like(heat),0.35+0.6*heat,0.05+0.7*heat**3],1)*life
    np.add.at(img,(yi,xi),col*6)
    im=Image.fromarray(np.clip(img*255,0,255).astype(np.uint8))
    g1=np.asarray(im.filter(ImageFilter.GaussianBlur(6)),np.float32)
    g2=np.asarray(im.filter(ImageFilter.GaussianBlur(22)),np.float32)
    out=img*255+g1*2.5+g2*3
    fl=max(0,1-t*2.5)*255  # flash
    out+=fl
    yy,xx=np.ogrid[:H,:W]; r=40+t*70; core=np.exp(-((xx-cx)**2+(yy-(cy-t*80))**2)/(2*r*r))*max(0,1-t/3)
    out+=core[...,None]*np.array([255,150,40])*1.3
    out[int(cy)+40:,:]*=0.25  # ground line darken
    return np.clip(out,0,255).astype(np.uint8)
def info(t):
    im=Image.new("RGB",(W,H),(8,12,22)); d=ImageDraw.Draw(im)
    for gx in range(0,W,40): d.line([(gx,0),(gx,H)],fill=(16,24,40))
    for gy in range(0,H,40): d.line([(0,gy),(W,gy)],fill=(16,24,40))
    d.text((W/2,150),"CASTLE BRAVO · 1954",font=fb(30),fill=(255,80,70),anchor="mm")
    base=720; bw=150; mx=15
    e=min(1,t/0.8); a=min(1,max(0,(t-0.6)/1.6))
    for i,(lab,val,c,p) in enumerate([("EXPECTED",6,(120,170,255),e),("ACTUAL",15,(255,170,40),a)]):
        x0=90+i*210; h=int(470*val/mx*(1-(1-p)**3))
        d.rounded_rectangle([x0,base-h,x0+bw,base],8,fill=c)
        d.text((x0+bw/2,base-h-40),f"{val*(1-(1-p)**3):.0f} MT",font=fb(38),fill=(255,255,255),anchor="mm")
        d.text((x0+bw/2,base+40),lab,font=fb(26),fill=(200,210,230),anchor="mm")
    if t>2.3:
        s=min(1,(t-2.3)/0.3); fs=int(60+40*s)
        d.text((W/2,840),"2.5x BIGGER",font=fb(min(64,fs)),fill=(255,220,60),anchor="mm")
    return np.asarray(im)
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(F),"-i","-","-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p","ornek.mp4"],stdin=subprocess.PIPE)
for n in range(N):
    t=n/F
    if t<3.3: fr=boom(t)
    elif t<3.7: a=(t-3.3)/0.4; fr=(boom(t)*(1-a)+info(t-3.3)*a).astype(np.uint8)
    else: fr=info(t-3.3)
    if t<3.5:
        im=Image.fromarray(fr); d=ImageDraw.Draw(im)
        d.text((W/2,120),"EXPECTED: 6 MEGATONS",font=fb(30),fill=(255,255,255),anchor="mm",stroke_width=3,stroke_fill=(0,0,0))
        fr=np.asarray(im)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
