from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np
F="/home/claude/oto-yukleme/assets/fonts/montserrat-latin-900.ttf"; AMBER=(245,166,35)
im=Image.open('/home/claude/space/ep02/img/ast-01-056.jpg').convert('RGB'); im=ImageEnhance.Contrast(im).enhance(1.12)
def base(W,H,zoom,fx,fy):
    s=max(W/im.width,H/im.height)*zoom; w,h=int(im.width*s),int(im.height*s)
    r=im.resize((w,h),Image.LANCZOS); x=int(min(max(fx*w-W/2,0),w-W)); y=int(min(max(fy*h-H/2,0),h-H)); return r.crop((x,y,x+W,y+H))
def txt(d,xy,t,sz,fill,anchor='mm',sw=12):
    d.text(xy,t,font=ImageFont.truetype(F,sz),fill=fill,anchor=anchor,stroke_width=sw,stroke_fill='black')
# vertical cover 1080x1920 : image lower-middle, text in top 75% (y<=1440), margins >=54 px, bottom 15% (>=1632) empty
W,H=1080,1920
bgi=base(W,H,1.0,0.5,0.5).filter(ImageFilter.GaussianBlur(40)); bgi=ImageEnhance.Brightness(bgi).enhance(0.4)
sq=im.resize((1080,1080),Image.LANCZOS); bgi.paste(sq,(0,520)); b=np.asarray(bgi).astype(np.float32)
yy=np.arange(H)[:,None,None]; b=b*(1-np.clip(1-yy/760,0,1)*0.65)*(1-np.clip((yy-1500)/420,0,1)*0.55)
c=Image.fromarray(np.clip(b,0,255).astype(np.uint8)); d=ImageDraw.Draw(c)
txt(d,(W/2,390),"23 DAYS",190,AMBER)
txt(d,(W/2,585),"IN ORBIT",170,'white')
c.save('/home/claude/space/ep02/cover.jpg',quality=92)
# thumbnail 1280x720
W,H=1280,720
b=np.asarray(base(W,H,1.15,0.5,0.5)).astype(np.float32); xx=np.arange(W)[None,:,None]; b=b*(1-np.clip(1-xx/700,0,1)*0.7)
t=Image.fromarray(np.clip(b,0,255).astype(np.uint8)); d=ImageDraw.Draw(t)
txt(d,(70,250),"23 DAYS",170,AMBER,anchor='lm'); txt(d,(70,430),"IN ORBIT",150,'white',anchor='lm')
t.save('/home/claude/space/ep02/thumbnail.jpg',quality=92)
Image.open('/home/claude/space/ep02/cover.jpg').resize((360,640)).save('/home/claude/space/ep02/prev/cover_prev.jpg',quality=80)
