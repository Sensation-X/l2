import os, shutil
SITE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(SITE, "dist")
L2 = os.path.join(DIST, "l2")

LANDING = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Хурмыч — медиапроект об играх</title>
  <meta name="description" content="Хурмыч — авторский проект о MMORPG: Lineage 2 и других играх. Гайды, патчи, экономика без воды.">
  <link rel="icon" href="/l2/assets/img/tg_avatar_512.png">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #14161C; color: #F2E8D5; line-height: 1.6; }
    .container { max-width: 800px; margin: 0 auto; padding: 60px 20px; text-align: center; }
    h1 { font-size: 3rem; margin-bottom: 20px; color: #EB7A34; }
    .tagline { font-size: 1.3rem; margin-bottom: 40px; color: #B9AFA3; }
    .games { display: grid; gap: 20px; margin: 40px 0; }
    .game-card { background: #1B1E26; border: 2px solid #232734; border-radius: 12px; padding: 30px; text-decoration: none; color: #F2E8D5; transition: border-color 0.3s; }
    .game-card:hover { border-color: #EB7A34; }
    .game-card h2 { color: #EB7A34; margin-bottom: 10px; }
    .game-card p { color: #B9AFA3; }
    .social { margin-top: 50px; }
    .social a { display: inline-block; margin: 0 10px; color: #EB7A34; text-decoration: none; font-weight: 600; }
    .footer { margin-top: 60px; color: #B9AFA3; font-size: 0.9rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>ХУРМЫЧ</h1>
    <p class="tagline">Авторский медиапроект об MMORPG. Гайды, патчи, экономика — без воды.</p>
    <div class="games">
      <a href="/l2/" class="game-card">
        <h2>Lineage 2</h2>
        <p>Essence и Main на Фогейме. Разборы обновлений, классы, экономика, промокоды.</p>
      </a>
    </div>
    <div class="social">
      <a href="https://t.me/hurmych">Telegram</a>
      <a href="https://www.youtube.com/@hurmych">YouTube</a>
    </div>
    <div class="footer">
      <p>© 2026 Хурмыч. Не является официальным ресурсом.</p>
    </div>
  </div>
</body>
</html>"""

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
            if not fn.endswith((".html", ".xml", ".txt")):
                continue
            p = os.path.join(root, fn)
            s = open(p, encoding="utf-8").read()
            s = s.replace("https://hurmych.ru/", "https://hurmych.ru/l2/")
            s = s.replace('"/assets', '"/l2/assets')
            open(p, "w", encoding="utf-8").write(s)
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(LANDING)
    print("Готово: лендинг в dist/index.html, контент L2 в dist/l2/")

main()
