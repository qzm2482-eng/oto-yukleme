from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np, random
F="/home/claude/oto-yukleme/assets/fonts/montserrat-latin-900.ttf"
W,H=1080,1920; HX,HY=1120,470; Z=1.15; random.seed(5)
im=Image.open('blitz.jpg').convert('RGB'); sw,sh=im.size
s=H/sh*Z; cw,ch=W/s,H/s; x0=min(max(HX-cw/2,0),sw-cw); y0=min(max(HY-ch*0.55,0),sh-ch)
sharp=im.transform((W,H),Image.AFFINE,(1/s,0,x0,0,1/s,y0),Image.BICUBIC)
sharp=ImageEnhance.Contrast(sharp).enhance(1.35); sharp=ImageEnhance.Sharpness(sharp).enhance(2.0)
blur=sharp.filter(ImageFilter.GaussianBlur(5))
hx=(HX-x0)*s; hy=(HY-y0)*s
yy,xx=np.mgrid[0:H,0:W]; r=np.hypot(xx-hx,(yy-hy)*1.1)
m=np.clip((r-320)/300,0,1)[...,None]   # sharp in centre, blur outside
a=np.asarray(sharp)*(1-m)+np.asarray(blur)*m; a=a/255
lum=a.mean(2,keepdims=True); a=a+np.concatenate([(lum-0.5)*0.2,(lum-0.5)*0.02,-(lum-0.5)*0.18],2)
a=a*(1-0.55*np.clip(r/1100,0,1))[...,None]                               # radial darkening
a=a+np.exp(-(r/230)**2)[...,None]*np.array([0.6,0.7,1.0])*0.35              # hot impact glow
a=a*(1-np.clip(1-yy/650,0,1)[...,None]*0.85)
bg=Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(bg,'RGBA')
for _ in range(120):
    ang=random.uniform(0,6.28); dist=random.uniform(120,520); x=hx+np.cos(ang)*dist; y=hy+np.sin(ang)*dist*0.85; L=random.uniform(10,40)
    d.line([(x,y),(x+np.cos(ang)*L,y+np.sin(ang)*L)],fill=(255,random.randint(160,235),90,random.randint(160,255)),width=random.choice([3,4,5]))
d.ellipse([hx-250,hy-215,hx+250,hy+215],outline=(255,35,35),width=16)
# inset: whole station for context
ins=Image.open('padA.jpg').convert('RGB'); ins=ImageEnhance.Contrast(ins).enhance(1.2).resize((330,462))
mk=Image.new('L',ins.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,329,461],26,fill=255)
ix,iy=70,1180; d.rounded_rectangle([ix-8,iy-8,ix+338,iy+470],32,fill=(255,255,255,255)); bg.paste(ins,(ix,iy),mk)
d.line([(ix+300,iy+40),(hx-120,hy+200)],fill=(255,35,35),width=12)
d.polygon([(hx-120,hy+200),(hx-175,hy+225),(hx-140,hy+265)],fill=(255,35,35))
f3=ImageFont.truetype(F,40); d.rounded_rectangle([ix,iy+396,ix+330,iy+462],0,fill=(0,0,0,170)); d.text((ix+165,iy+429),"APOLLO 12",font=f3,fill='white',anchor='mm')
f1=ImageFont.truetype(F,160); f2=ImageFont.truetype(F,52)
lab="APOLLO 12 · 1969"; tw=d.textlength(lab,font=f2)
d.rounded_rectangle([W/2-tw/2-30,170,W/2+tw/2+30,250],radius=20,fill=(210,20,20)); d.text((W/2,210),lab,font=f2,fill='white',anchor='mm')
d.text((W/2,375),"STRUCK",font=f1,fill='white',anchor='mm',stroke_width=10,stroke_fill='black')
d.text((W/2,540),"TWICE!",font=f1,fill=(255,214,0),anchor='mm',stroke_width=10,stroke_fill='black')
bg=bg.filter(ImageFilter.UnsharpMask(2,50,3)); bg.save('cover.jpg',quality=92); bg.resize((540,960)).save('cover_prev.jpg',quality=75)
print(int(hx),int(hy))
