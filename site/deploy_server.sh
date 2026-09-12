#!/usr/bin/env bash
# ============================================================
#  deploy_server.sh v2 — ИЗОЛИРОВАННЫЙ деплой сайта hurmych.ru
#
#  Гарантии изоляции:
#    - ничего не удаляет и не отключает (в т.ч. default-сайт nginx);
#    - создаёт ТОЛЬКО свой конфиг hurmych и свою папку /var/www/hurmych;
#    - nginx ставится, только если его нет;
#    - сертификат выпускается через certonly --webroot (не правит чужие конфиги);
#    - перед каждым reload проверяет конфиг (nginx -t): при ошибке не перезагружает.
#
#  Подготовка с ПК (PowerShell из D:\L2_media):
#    scp -r site\dist root@31.207.75.248:/root/site_dist
#    scp site\deploy_server.sh root@31.207.75.248:/root/
#  Запуск на сервере:
#    bash /root/deploy_server.sh твоя@почта.ru
#
#  Требование: DNS A-записи hurmych.ru и www указывают на IP сервера.
# ============================================================
set -e
EMAIL="${1:?Укажи почту: bash /root/deploy_server.sh you@mail.ru}"
DOMAIN="hurmych.ru"
WWW="/var/www/hurmych"
ART="/root/hurmych"

echo "== [1/6] nginx (ставлю, только если отсутствует) =="
if command -v nginx >/dev/null 2>&1; then
  echo "nginx уже установлен: $(nginx -v 2>&1)"
else
  apt-get update -y && apt-get install -y nginx
fi

echo "== [2/6] Папки и файлы сайта =="
mkdir -p "$WWW" "$ART"
cp -r /root/site_dist/. "$WWW/"
cp -r /root/site_dist "$ART/dist_backup_$(date +%F)" 2>/dev/null || true
chown -R www-data:www-data "$WWW" 2>/dev/null || true
ls "$WWW" | head -8

echo "== [3/6] Конфиг сайта (только свой файл) =="
if [ -d /etc/nginx/sites-enabled ]; then
  CONF="/etc/nginx/sites-available/hurmych"
  mkdir -p /etc/nginx/sites-available
  ln -sf "$CONF" /etc/nginx/sites-enabled/hurmych
else
  CONF="/etc/nginx/conf.d/hurmych.conf"
fi

cat > "$CONF" <<CONF
# сайт hurmych.ru — изолированный блок, создан deploy_server.sh
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    root $WWW;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
    location ~* \.(png|jpe?g|webp|svg|css|js|xml|txt|ico)$ {
        expires 7d;
        add_header Cache-Control "public";
    }
    gzip on;
    gzip_types text/css application/javascript application/rss+xml image/svg+xml text/html;
}
CONF
nginx -t && systemctl reload nginx
echo "конфиг применён: $CONF"

echo "== [4/6] HTTPS-сертификат (certonly, чужие конфиги не трогаю) =="
if [ ! -x "$(command -v certbot)" ]; then
  apt-get install -y certbot
fi
certbot certonly --webroot -w "$WWW" -d "$DOMAIN" -d "www.$DOMAIN" \
  --agree-tos -m "$EMAIL" -n || echo "!! сертификат не выпущен (DNS ещё не разошёлся?) — сайт работает по http, повтори позже"

echo "== [5/6] Включаю HTTPS, если сертификат появился =="
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  cat > "$CONF" <<CONF
# сайт hurmych.ru — изолированный блок, создан deploy_server.sh
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    location /.well-known/acme-challenge/ { root $WWW; }
    location / { return 301 https://\$host\$request_uri; }
}
server {
    listen 443 ssl;
    http2 on;
    server_name $DOMAIN www.$DOMAIN;
    root $WWW;
    index index.html;

    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    location / {
        try_files \$uri \$uri/ =404;
    }
    location ~* \.(png|jpe?g|webp|svg|css|js|xml|txt|ico)$ {
        expires 7d;
        add_header Cache-Control "public";
    }
    gzip on;
    gzip_types text/css application/javascript application/rss+xml image/svg+xml text/html;
}
CONF
  nginx -t && systemctl reload nginx
  echo "HTTPS включён"
else
  echo "сертификата нет — оставляю http; команда для повтора:"
  echo "  certbot certonly --webroot -w $WWW -d $DOMAIN -d www.$DOMAIN"
fi

echo "== [6/6] Проверка =="
curl -sI -H "Host: $DOMAIN" http://127.0.0.1/ | head -3 || true
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  curl -sI "https://$DOMAIN/" | head -3 || true
fi
echo
echo "Готово. Изменены только: $CONF, $WWW, $ART"
echo "Открой: https://$DOMAIN  (или http://$DOMAIN пока без сертификата)"
echo "Обновление контента: scp -r site\\dist\\* root@IP:$WWW/"
