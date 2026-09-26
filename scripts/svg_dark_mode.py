"""Add a prefers-color-scheme: dark palette to SVG diagrams (idempotent).

Usage: python3 scripts/svg_dark_mode.py images/<domain>/<date>/*.svg
"""
import re, sys, colorsys
NAMED={"white":"#ffffff","black":"#000000"}
MARK="/* auto dark mode */"
def parse(c):
    c=c.strip().lower()
    if c in NAMED: c=NAMED[c]
    m=re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})",c)
    if m:
        h=m[1]; h="".join(x*2 for x in h) if len(h)==3 else h
        return tuple(int(h[i:i+2],16)/255 for i in (0,2,4)),None
    m=re.fullmatch(r"rgba?\(([^)]*)\)",c)
    if m:
        p=[x.strip() for x in m[1].split(",")]
        rgb=tuple(float(x.rstrip('%'))/(100 if x.endswith('%') else 255) for x in p[:3]); a=p[3] if len(p)>3 else None
        return rgb,a
    return None,None
def dark(c):
    rgb,a=parse(c)
    if rgb is None: return None
    h,l,s=colorsys.rgb_to_hls(*rgb)
    if l>=0.8:
        if s<0.12: h,s=0.54,0.2          # neutral paper -> site dark surface hue
        l2=0.115+(1-l)*0.55; s2=max(s*0.45,0.12) if s<0.2 else s*0.45
    elif s>0.45 and l>=0.2:              # saturated accent: keep hue, lift
        l2=min(max(l+0.25,0.58),0.72); s2=min(s,0.75)
    elif l<=0.4:
        if s<0.12: h,s=0.52,0.08          # neutral ink -> site light ink
        l2=0.90-l*0.35; s2=s*0.6
    elif s>0.25: l2=min(max(l+0.12,0.55),0.72); s2=s
    else:        l2=min(max(1.1-l,0.35),0.7); s2=s
    r,g,b=colorsys.hls_to_rgb(h,l2,s2)
    hx="#%02x%02x%02x"%tuple(round(v*255) for v in (r,g,b))
    if a is not None: return "rgba(%d,%d,%d,%s)"%(round(r*255),round(g*255),round(b*255),a)
    return hx
COLOR=r"#[0-9a-fA-F]{3,6}\b|rgba?\([^)]*\)|\bwhite\b|\bblack\b"
def convert(t):
    if MARK in t: return None
    rules=[]
    # presentation attributes
    for attr in ("fill","stroke","stop-color","flood-color"):
        for val in sorted(set(re.findall(r'\s%s="([^"]+)"'%attr,t))):
            d=dark(val)
            if d: rules.append('[%s="%s" i]{%s:%s}'%(attr,val,attr,d))
    # <style> rules
    for block in re.findall(r"<style[^>]*>(.*?)</style>",t,re.S):
        block=re.sub(r"/\*.*?\*/","",block,flags=re.S)
        for sel,decls in re.findall(r"([^{}@]+)\{([^{}]*)\}",block):
            out=[]
            for prop,val in re.findall(r"([\w-]+)\s*:\s*([^;]+)",decls):
                if prop in("fill","stroke","stop-color","color","flood-color") and re.search(COLOR,val):
                    nv=re.sub(COLOR,lambda m:dark(m[0]) or m[0],val); out.append(f"{prop}:{nv}")
            if out: rules.append(f"{sel.strip()}{{{';'.join(out)}}}")
    # inline style attributes
    for val in sorted(set(re.findall(r'\sstyle="([^"]+)"',t))):
        for prop,col in re.findall(r"(fill|stroke|stop-color)\s*:\s*(%s)"%COLOR,val):
            d=dark(col)
            if d: rules.append('[style*="%s:%s"]{%s:%s !important}'%(prop,col,prop,d))
    rules.insert(0,"svg:not([fill]){fill:%s}"%dark("#000"))
    css="<style>%s@media (prefers-color-scheme: dark){%s}</style>"%(MARK,"".join(rules))
    i=t.rindex("</svg>")
    return t[:i]+css+"\n"+t[i:]
if __name__=="__main__":
    n=0
    for f in sys.argv[1:]:
        t=open(f,encoding="utf-8").read(); r=convert(t)
        if r: open(f,"w",encoding="utf-8").write(r); n+=1
    print("converted",n,"of",len(sys.argv)-1)
