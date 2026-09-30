import sys, numpy as np
from PIL import Image
from engine import Engine
E = Engine()
W,H = E.W, E.H
def rose_frame(name, camH=2.6, shape=1.2, color=1.2, bleed=0.0, light=1.0, hole=0.0, motes=0.0, sat=1.0, camPos=(0,0), post=None):
    camH=float(camH)
    E.fb_hdr.use(); E.ctx.clear(0,0,0,1)
    E.draw('scene_rose.frag', E.fb_hdr, uRes=(float(W),float(H)), uTime=3.0, uT=3.0, uCamPos=camPos, uCamH=camH, uCamRot=0.0,
           uShape=shape, uColor=color, uBleed=bleed, uLight=light, uLightPos=(0.25,0.35), uVoice=0.0, uHole=hole,
           uTexMode=0.0, uWall=1.0, uSat=sat, uDim=0.0, uMotes=motes, uPxWorld=camH/H)
    P = dict(thresh=0.9, uBloom=0.7, rays=0.35, rayCenter=(0.5,0.5), uTime=3.0)
    if post: P.update(post)
    img = E.post(E.hdr, P)
    Image.fromarray(img).save(f'stills/{name}.png')
rose_frame('rose_full')
rose_frame('rose_close', camH=0.9, camPos=(0.3,0.45))
rose_frame('rose_draw', shape=0.55, color=0.0)
rose_frame('rose_fill', shape=1.2, color=0.5)
rose_frame('rose_bleed', bleed=0.8)
rose_frame('rose_clear', color=0.0)
