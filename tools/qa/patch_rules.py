import re
p='elections.py'
s=open(p,encoding='utf-8').read()

# 1. dual-link TIP button and violation recording
s=s.replace('''def tip_button(c):
    t = c.get("tip")
    if t and t.get("url"):
        return f'<a class="btn-o" href="{e(t["url"])}" rel="noopener">View on TIP →</a>'
    return '<span class="btn-o off" aria-disabled="true">No TIP record yet</span>\'''','''CUR = [""]          # page currently being built (for publishing-rule reporting)
VIOL = []           # (page, rule, detail)

def violate(rule, detail):
    item = (CUR[0], rule, detail)
    if item not in VIOL:
        VIOL.append(item)

def tip_button(c):
    t = c.get("tip")
    if t and t.get("url"):
        if t.get("grades_url"):
            return (f'<a class="btn-o" href="{e(t["grades_url"])}" rel="noopener">View congressional record on TIP →</a>'
                    f'<span class="small"><a href="{e(t["url"])}" rel="noopener">TIP governor profile ↗</a></span>')
        return f'<a class="btn-o" href="{e(t["url"])}" rel="noopener">View on TIP →</a>'
    violate("R1 no TIP profile", c["name"])
    return '<span class="btn-o off" aria-disabled="true">No TIP record yet</span>\'''')
open(p,'w',encoding='utf-8').write(s)
