#!/usr/bin/env bash
# ============================================================
#  recon.sh — РАЗВЕДКА сервера. ТОЛЬКО ЧИТАЕТ, ничего не меняет.
#  Запуск с ПК:  ssh root@31.207.75.248 "bash -s" < site\recon.sh
#  Вывод целиком прислать в чат.
# ============================================================
echo "===== 1. ОС ====="
head -3 /etc/os-release 2>/dev/null
uname -r

echo; echo "===== 2. Какие веб-серверы установлены ====="
for c in nginx apache2 httpd caddy; do
  if command -v "$c" >/dev/null 2>&1; then
    echo "--- $c: $($c -v 2>&1 | head -1)"
  fi
done

echo; echo "===== 3. Кто слушает порты (80/443 и остальные) ====="
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | head -25

echo; echo "===== 4. Включённые конфиги nginx ====="
ls -la /etc/nginx/sites-enabled/ 2>/dev/null
ls -la /etc/nginx/conf.d/ 2>/dev/null

echo; echo "===== 5. server_name / listen / root во включённых конфигах ====="
for f in /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf; do
  [ -e "$f" ] || continue
  echo "--- $f"
  grep -E "server_name|listen|root " "$f" 2>/dev/null | sed 's/^[ \t]*//'
done

echo; echo "===== 6. Содержимое /var/www ====="
ls -la /var/www/ 2>/dev/null

echo; echo "===== 7. Запущенные сервисы ====="
systemctl list-units --type=service --state=running --no-pager 2>/dev/null | head -30

echo; echo "===== 8. Есть ли уже сертификаты Let's Encrypt ====="
ls /etc/letsencrypt/live/ 2>/dev/null || echo "нет"

echo; echo "===== 9. Ресурсы ====="
df -h / | tail -1
free -h | head -2

echo; echo "===== 10. Где лежит существующий проект (по root в конфигах) ====="
grep -RE "root\s+/|alias\s+/" /etc/nginx/sites-enabled/ /etc/nginx/conf.d/ /etc/apache2/sites-enabled/ 2>/dev/null | head -20

echo; echo "===== РАЗВЕДКА ЗАВЕРШЕНА (ничего не изменено) ====="
