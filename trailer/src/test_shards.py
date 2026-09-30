import numpy as np
from PIL import Image
from engine import Engine
from shards import ShardRenderer, camera_for, IMPACT
E = Engine(); W,H = E.W,E.H
S = ShardRenderer(E.ctx)
print('shards', len(S.shards), 'verts', S.n)
rose_u = dict(uTime=3.0, uT=3.0, uCamPos=(0.0,0.0), uCamH=2.6, uCamRot=0.0, uShape=1.2, uColor=1.2, uBleed=0.25,
              uLight=1.0, uLightPos=(0.25,0.35), uVoice=0.0, uHole=0.0, uWall=1.0, uSat=1.0, uDim=0.0, uMotes=0.0)
S.bake_window(E, **rose_u)
def shot(name, tau, camPos=(0,0), camH=2.6, crackR=0.0, crackGlow=0.0, tilt=(0,0), dolly=0.0, hole=1.0, drift=0.0, wall=1.0, light=1.0):
    u = dict(rose_u); u.update(uCamPos=camPos, uCamH=camH, uHole=hole, uTexMode=0.0, uWall=wall, uLight=light)
    E.draw('scene_rose.frag', E.fb_hdr, uRes=(float(W),float(H)), uPxWorld=camH/H, **u)
    VP, eye = camera_for(camPos, camH, W/H, tilt=tilt, dolly=dolly)
    S.draw(E.fb_hdr, VP, eye, tau, crackR=crackR, crackGlow=crackGlow, drift=drift)
    img = E.post(E.hdr, dict(thresh=0.9, uBloom=0.7, uTime=3.0, rays=0.4, rayCenter=(0.5,0.5)))
    Image.fromarray(img).save(f'stills/{name}.png')
shot('sh_rest', 0.0, hole=1.0)
shot('sh_crack', 0.0, crackR=0.45, crackGlow=1.0)
shot('sh_t05', 0.5)
shot('sh_t15', 1.5, camH=2.9)
shot('sh_frozen', 3.0, camPos=(0.2,0.1), camH=2.0, dolly=1.8, tilt=(0.3,0.2), drift=2.0, wall=0.0, light=0.3)
