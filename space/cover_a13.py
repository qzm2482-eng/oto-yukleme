from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np
F="/home/claude/oto-yukleme/assets/fonts/montserrat-latin-900.ttf"; D='/home/claude/space/apollo13/'
W,H=1080,1920
im0=Image.open(D+'img/AS13-62-8929.jpg').convert('RGB')
PAD=1400                           # reflect-pad the top so the canister can sit lower than the title block
im=Image.fromarray(np.pad(np.asarray(im0),((PAD,0),(0,0),(0,0)),mode='reflect')); sw,sh=im.size
CX,CY=1690,1597+PAD                # canister centre in (padded) source px
cw=2300; ch=cw*H/W
x0=CX-cw*0.50; y0=CY-ch*(960/H)
s=W/cw
sharp=im.transform((W,H),Image.AFFINE,(cw/W,0,x0,0,ch/H,y0),Image.BICUBIC)
sharp=ImageEnhance.Contrast(sharp).enhance(1.15)
hx,hy=(CX-x0)*s,(CY-y0)*s
blur=sharp.filter(ImageFilter.GaussianBlur(7))
yy,xx=np.mgrid[0:H,0:W]; r=np.hypot(xx-hx,(yy-hy)*1.0)
m=np.clip((r-300)/300,0,1)[...,None]
a=(np.asarray(sharp)*(1-m)+np.asarray(blur)*m)/255
a=a*(1-0.50*np.clip(r/1250,0,1))[...,None]                         # vignette
top=np.clip(1-yy/650,0,1)[...,None]; a=a*(1-0.62*top)              # darken top for title
bot=np.clip((yy-1250)/670,0,1)[...,None]; a=a*(1-0.5*bot)
bg=Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(bg,'RGBA')
# red ring on canister
rx,ry=330,310
d.ellipse([hx-rx,hy-ry,hx+rx,hy+ry],outline=(255,35,35),width=18)
# inset (context: the lander)
ins=Image.open(D+'img/AS13-59-8562.jpg').convert('RGB'); ins=ImageEnhance.Contrast(ins).enhance(1.1)
ins=ins.crop((0,0,ins.width,ins.height)).resize((300,300),Image.LANCZOS)
mk=Image.new('L',ins.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,279,279],26,fill=255)
ix,iy=74,1310
d.rounded_rectangle([ix-9,iy-9,ix+289,iy+289],34,fill=(255,255,255,255)); bg.paste(ins,(ix,iy),mk)
# title
f1=ImageFont.truetype(F,104); f2=ImageFont.truetype(F,128)
d.text((W/2,330),"SQUARE FILTER",font=f1,fill='white',anchor='mm',stroke_width=10,stroke_fill='black')
w1=d.textlength("ROUND ",font=f2); w2=d.textlength("HOLE",font=f2); x=(W-(w1+w2))/2
d.text((x,490),"ROUND ",font=f2,fill='white',anchor='lm',stroke_width=10,stroke_fill='black')
d.text((x+w1,490),"HOLE",font=f2,fill=(245,166,35),anchor='lm',stroke_width=10,stroke_fill='black')
bg=bg.filter(ImageFilter.UnsharpMask(2,40,3)); bg.save(D+'cover.jpg',quality=93)
print(bg.size,int(hx),int(hy),rx,ry,d.textlength("SQUARE FILTER",font=f1),w1+w2)
