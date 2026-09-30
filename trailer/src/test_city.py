import sys
from PIL import Image
from engine import Engine
from scenes import city_uniforms, set_city_arrays
E = Engine(); W,H = E.W, E.H
def city(name, camPos=(0,0.05), camH=1.3, t=5.0, post=None, **kw):
    p,_ = E.prog('scene_city.frag'); set_city_arrays(p)
    u = city_uniforms(**kw)
    E.draw('scene_city.frag', E.fb_hdr, uRes=(float(W),float(H)), uTime=t, uT=t, uCamPos=camPos, uCamH=camH, **u)
    P = dict(thresh=0.8, uBloom=0.8, uTime=t)
    if post: P.update(post)
    Image.fromarray(E.post(E.hdr, P)).save(f'stills/{name}.png')
city('city_dusk', sky='dusk', uFore=1.0, uBench=1.0, camPos=(0.2, 0.12), camH=1.9, uLamps=0.6)
city('city_night_links', sky='night', uLinks=1.0, camPos=(0.4,0.1), camH=1.6)
city('city_bleed', sky='blood', uLinks=1.0, uBleed=1.0, camPos=(0.8,0.1), camH=1.2)
city('city_shatter', sky='night', uLinks=1.0, uBleed=1.0, uShatter=0.9, camPos=(0.8,0.1), camH=1.4)
city('city_dawn_ships', sky='dawn', uLamps=0.0, uBroken=1.0, uSmoke=0.6, uShips=6.0, uSunPos=(0.9, 0.05), camPos=(0.3,0.2), camH=1.8)
city('city_ghost', sky='night', uGhost=1.0, uLamps=0.3, camPos=(0.8,0.1), camH=1.3)
