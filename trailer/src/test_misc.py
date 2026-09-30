import numpy as np, moderngl
from PIL import Image
from engine import Engine
import typo
E = Engine(); W,H = E.W,E.H
tree = typo.make_tree()
tree.save('stills/tree.png')
ttex = E.ctx.texture(tree.size, 4, np.asarray(tree).tobytes()); ttex.build_mipmaps(); ttex.filter=(moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
def save(name, P, ov=None):
    Image.fromarray(E.post(E.hdr, P, overlay=ov)).save(f'stills/{name}.png')
# garden
ttex.use(1)
E.draw('scene_garden.frag', E.fb_hdr, uRes=(float(W),float(H)), uTime=4.0, uCamPos=(0.0,0.0), uCamH=0.9, uTree=1, uVoice=0.3, uPane=1.0, uMist=1.0, uMoon=1.0, uFireflies=1.0, uTint=(1,1,1))
save('garden', dict(thresh=0.7, uBloom=0.9, rays=0.5, rayCenter=(0.5+(-0.55)/0.9*H/W, 0.5+0.36/0.9), uTime=4.0))
# void
E.draw('scene_void.frag', E.fb_hdr, uRes=(float(W),float(H)), uTime=4.0, uBeam=1.0, uBeamX=0.1, uBeamTilt=0.2, uDust=1.0, uBeamCol=(1.0,0.85,0.65), uBg=(0.01,0.01,0.015), uGlowR=0.0, uGlowCol=(0,0,0))
ov = typo.Overlay(); typo.draw_card(ov, '빛에 기억을 담던 왕국', 2.0, 5.0)
typo.draw_subtitle(ov, '다른 것은 거의 남지 않았는데, 왜 유리만 이렇게 많은지 궁금할지도 모르겠습니다.', 1.0)
save('void_card', dict(thresh=0.8, uBloom=0.6, uTime=4.0), ov.result())
# title
m = typo.title_mask('글리미스 이야기')
mt = E.ctx.texture((W,H), 4, m.tobytes())
mt.use(1)
E.draw('scene_title.frag', E.fb_hdr, uRes=(float(W),float(H)), uTime=4.0, uMask=1, uReveal=1.0, uSweep=0.5, uGlow=0.6, uBeam=1.0)
ov = typo.Overlay(); typo.draw_card(ov, 'TALES OF GLIMMITH', 2.0, 5.0, size=40, weight=500, y=H*0.63, color=(225,190,130), fontname='Cinzel.ttf', track0=0.3, track1=0.4, glow_amt=0.4)
save('title', dict(thresh=0.8, uBloom=0.8, uTime=4.0), ov.result())
