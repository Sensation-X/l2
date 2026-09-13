import os, re, shutil
SITE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(SITE, "dist")
L2 = os.path.join(DIST, "l2")
LANDING_SRC = os.path.join(SITE, "landing", "index.html")

def fix_html(s):
    s = s.replace("https://hurmych.ru/", "https://hurmych.ru/l2/")
    s = s.replace('content="assets/', 'content="/l2/assets/')
    s = re.sub(r'(href|src)="(?!/|https?:|#|mailto:)([^"]+)"', r'\1="/l2/\2"', s)
    return s

def main():
    if os.path.exists(L2):
        shutil.rmtree(L2)
    os.makedirs(L2)
    for name in os.listdir(DIST):
        if name == "l2":
            continue
        shutil.move(os.path.join(DIST, name), os.path.join(L2, name))
    for root, dirs, files in os.walk(L2):
        for fn in files:
            p = os.path.join(root, fn)
            if fn.endswith(".html"):
                s = open(p, encoding="utf-8").read()
                open(p, "w", encoding="utf-8").write(fix_html(s))
            elif fn.endswith((".xml", ".txt")):
                s = open(p, encoding="utf-8").read()
                s = s.replace("https://hurmych.ru/", "https://hurmych.ru/l2/")
                open(p, "w", encoding="utf-8").write(s)
    if os.path.exists(LANDING_SRC):
        shutil.copy(LANDING_SRC, os.path.join(DIST, "index.html"))
    else:
        print("ВНИМАНИЕ: site/landing/index.html не найден, лендинг не создан")
    print("Готово: лендинг в dist/index.html, контент L2 в dist/l2/")

main()