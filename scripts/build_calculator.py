#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка Калькулятор_дохода.xlsx для проекта L2-медиа."""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "Калькулятор_дохода.xlsx")

H1 = Font(bold=True, size=14, color="FFFFFF")
H2 = Font(bold=True, size=11, color="FFFFFF")
BOLD = Font(bold=True)
SMALL = Font(size=9, italic=True, color="666666")
FILL_H1 = PatternFill("solid", fgColor="1F3864")
FILL_H2 = PatternFill("solid", fgColor="2E75B6")
FILL_IN = PatternFill("solid", fgColor="FFF2CC")   # жёлтый = редактируемый ввод
FILL_OUT = PatternFill("solid", fgColor="E2EFDA")  # зелёный = расчёт
FILL_GREY = PatternFill("solid", fgColor="F2F2F2")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

MONEY = '#,##0" ₽"'
NUM = '#,##0'
PCT = '0.0%'


def title(ws, text, span=6):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value=text)
    c.font = H1
    c.fill = FILL_H1
    c.alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 26


def head(ws, row, values, start=1):
    for i, v in enumerate(values):
        c = ws.cell(row=row, column=start + i, value=v)
        c.font = H2
        c.fill = FILL_H2
        c.alignment = CENTER
        c.border = BOX
    ws.row_dimensions[row].height = 32


def widths(ws, w):
    for i, width in enumerate(w, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width


wb = Workbook()

# ============================================================ ЛИСТ 1: ВВОД
ws = wb.active
ws.title = "Ввод"
widths(ws, [46, 16, 16, 60])
title(ws, "ВВОД ДАННЫХ — редактируй только жёлтые ячейки", 4)
ws["A2"] = "Жёлтые ячейки = твои допущения. Зелёные на других листах = расчёт по формулам."
ws["A2"].font = SMALL

rows = [
    ("SECTION", "TELEGRAM", None, None, None),
    ("Подписчиков в Telegram", 800, NUM, "Пороги рангов партнёрки: D=350, C=500, B=1000, A=2500, S=5000"),
    ("Средний охват одного поста", 700, NUM, "Для рангов: D=500, C=750, B=1000, A=1500, S=3000"),
    ("CPM ниши (₽ за 1000 просмотров поста)", 150, MONEY, "Игровая ниша в TG: ориентир 100–300 ₽"),
    ("Продажных интеграций в месяц", 2, NUM, "0 на старте; реально с 500–1000 подписчиков"),
    ("SECTION", "ВИДЕОПЛОЩАДКИ", None, None, None),
    ("Rutube: просмотров в месяц", 6000, NUM, "Порог монетизации: самозанятый + 2 видео + 5000 просмотров"),
    ("Rutube: ставка ₽ / 1000 просмотров", 60, MONEY, "Ориентир 50–90 ₽"),
    ("VK Видео: просмотров в месяц", 0, NUM, "Порог: 5000 подписчиков сообщества, охваты ≥30%"),
    ("VK Видео: ставка ₽ / 1000 просмотров", 40, MONEY, "Ориентир 30–50 ₽ (50–80% rev share)"),
    ("YouTube: просмотров в месяц", 25000, NUM, "Монетизация AdSense в РФ отключена → доход 0 ₽. Нужно для партнёрки"),
    ("SECTION", "ДЗЕН", None, None, None),
    ("Дзен: просмотров статей в месяц", 40000, NUM, "Порог монетизации: 30 часов просмотра от подписчиков за 30 дней"),
    ("Доля дочитываний", 0.3, PCT, "Обычно 20–40%"),
    ("Средняя длительность дочитывания, мин", 2.5, '0.0', "Для гайдов 2–4 минуты"),
    ("Ставка ₽ за минуту дочитывания", 0.05, '0.00', "Ориентир 0,05 ₽"),
    ("SECTION", "ПОДПИСКИ И ДОНАТЫ", None, None, None),
    ("Boosty/клуб: платящих подписчиков", 5, NUM, "Реалистично 1–3% от аудитории"),
    ("Средний чек подписки, ₽/мес", 200, MONEY, "Тарифы 100 / 250 / 500 ₽"),
    ("Инфопродукты и консультации: продаж в месяц", 2, NUM, "PDF-гайды, разборы"),
    ("Средний чек продукта, ₽", 350, MONEY, "190–1500 ₽ в зависимости от продукта"),
    ("SECTION", "ПАРТНЁРКА ФОГЕЙМА (не кэш)", None, None, None),
    ("Охват всего контента за месяц (просмотры)", 60000, NUM, "TG + YouTube + VK + Rutube + Дзен"),
    ("CTR на реферальную ссылку", 0.005, PCT, "Реально 0,3–1% от всех просмотров; в постах про бонусы и промокоды до 3–5%"),
    ("Конверсия перехода в регистрацию", 0.35, PCT, "Ориентир 30–50%"),
    ("Доля новых/вернувшихся среди регистраций", 0.25, PCT, "Важно: твинки и действующие игроки не засчитываются"),
    ("Доля дошедших до нужного уровня", 0.5, PCT, "91 ур. в Essence/Legacy, 116 в Main"),
    ("Бонусов Фогейма за 1 реферала", 700, NUM, "Фиксировано правилами Программы"),
    ("Бонусов Фогейма за ранг в месяц", 6000, NUM, "Лимит: D=4000, C=10000, B=20000, A=40000, S=70000"),
    ("SECTION", "НАЛОГИ", None, None, None),
    ("Ставка НПД (самозанятый)", 0.06, PCT, "6% с юрлиц, 4% с физлиц"),
]

r = 3
INPUT = {}
for row in rows:
    if row[0] == "SECTION":
        ws.cell(row=r, column=1, value=row[1]).font = H2
        for col in range(1, 5):
            ws.cell(row=r, column=col).fill = FILL_H2
        ws.cell(row=r, column=1).font = H2
        r += 1
        continue
    label, value, fmt, note = row
    ws.cell(row=r, column=1, value=label).alignment = WRAP
    c = ws.cell(row=r, column=2, value=value)
    c.fill = FILL_IN
    c.number_format = fmt
    c.border = BOX
    c.font = BOLD
    ws.cell(row=r, column=4, value=note).font = SMALL
    ws.cell(row=r, column=4).alignment = WRAP
    INPUT[label] = f"'Ввод'!$B${r}"
    r += 1

ws.freeze_panes = "A3"

# ============================================================ ЛИСТ 2: РАСЧЁТ МЕСЯЦА
ws2 = wb.create_sheet("Расчёт месяца")
widths(ws2, [44, 18, 62])
title(ws2, "РАСЧЁТ ДОХОДА ЗА ОДИН МЕСЯЦ", 3)
head(ws2, 2, ["Источник", "Сумма", "Как считается / условие"])

I = INPUT
calc = [
    ("КАШ (живые деньги)", None, None, "section"),
    ("Telegram: продажа интеграций",
     f"={I['Средний охват одного поста']}/1000*{I['CPM ниши (₽ за 1000 просмотров поста)']}*{I['Продажных интеграций в месяц']}",
     "охват/1000 × CPM × число размещений", "money"),
    ("Rutube: монетизация",
     f"={I['Rutube: просмотров в месяц']}/1000*{I['Rutube: ставка ₽ / 1000 просмотров']}",
     "порог: самозанятый + 2 видео + 5000 просмотров", "money"),
    ("VK Видео: монетизация",
     f"={I['VK Видео: просмотров в месяц']}/1000*{I['VK Видео: ставка ₽ / 1000 просмотров']}",
     "порог: 5000 подписчиков сообщества, охваты ≥30%", "money"),
    ("YouTube: монетизация",
     "=0",
     "AdSense для авторов из РФ отключён → 0 ₽ (используется для охвата и партнёрки)", "money"),
    ("Дзен: дочитывания",
     f"={I['Дзен: просмотров статей в месяц']}*{I['Доля дочитываний']}*{I['Средняя длительность дочитывания, мин']}*{I['Ставка ₽ за минуту дочитывания']}",
     "просмотры × доля дочитываний × минуты × ставка; порог 30 ч просмотра от подписчиков", "money"),
    ("Boosty / платный клуб",
     f"={I['Boosty/клуб: платящих подписчиков']}*{I['Средний чек подписки, ₽/мес']}",
     "платящие × средний чек", "money"),
    ("Инфопродукты и консультации",
     f"={I['Инфопродукты и консультации: продаж в месяц']}*{I['Средний чек продукта, ₽']}",
     "продажи × средний чек", "money"),
]

r = 3
first_money = None
for label, formula, note, kind in calc:
    if kind == "section":
        ws2.cell(row=r, column=1, value=label).font = H2
        for col in range(1, 4):
            ws2.cell(row=r, column=col).fill = FILL_H2
        r += 1
        first_money = r
        continue
    ws2.cell(row=r, column=1, value=label).alignment = WRAP
    c = ws2.cell(row=r, column=2, value=formula)
    c.number_format = MONEY
    c.fill = FILL_OUT
    c.border = BOX
    ws2.cell(row=r, column=3, value=note).font = SMALL
    ws2.cell(row=r, column=3).alignment = WRAP
    r += 1
last_money = r - 1

ws2.cell(row=r, column=1, value="ИТОГО ДОХОД (грязными)").font = BOLD
c = ws2.cell(row=r, column=2, value=f"=SUM(B{first_money}:B{last_money})")
c.font = BOLD
c.number_format = MONEY
c.fill = FILL_OUT
gross = r
r += 1
ws2.cell(row=r, column=1, value=f"Налог НПД")
c = ws2.cell(row=r, column=2, value=f"=-B{gross}*{I['Ставка НПД (самозанятый)']}")
c.number_format = MONEY
tax = r
r += 1
ws2.cell(row=r, column=1, value="ЧИСТЫМИ НА РУКИ").font = Font(bold=True, size=12)
c = ws2.cell(row=r, column=2, value=f"=B{gross}+B{tax}")
c.font = Font(bold=True, size=12)
c.number_format = MONEY
c.fill = PatternFill("solid", fgColor="C6E0B4")
net = r
r += 2

ws2.cell(row=r, column=1, value="ПАРТНЁРКА ФОГЕЙМА (не кэш, а игровая ценность)").font = H2
for col in range(1, 4):
    ws2.cell(row=r, column=col).fill = FILL_H2
r += 1
ws2.cell(row=r, column=1, value="Переходов по реферальной ссылке")
c = ws2.cell(row=r, column=2, value=f"={I['Охват всего контента за месяц (просмотры)']}*{I['CTR на реферальную ссылку']}")
c.number_format = NUM
c.fill = FILL_OUT
clicks = r
r += 1
ws2.cell(row=r, column=1, value="Регистраций")
c = ws2.cell(row=r, column=2, value=f"=B{clicks}*{I['Конверсия перехода в регистрацию']}")
c.number_format = NUM
c.fill = FILL_OUT
regs = r
r += 1
ws2.cell(row=r, column=1, value="Из них новых/вернувшихся (твинки не считаются)")
c = ws2.cell(row=r, column=2, value=f"=B{regs}*{I['Доля новых/вернувшихся среди регистраций']}")
c.number_format = '0.0'
c.fill = FILL_OUT
newregs = r
r += 1
ws2.cell(row=r, column=1, value="Зачтённых рефералов (дошли до уровня)")
c = ws2.cell(row=r, column=2, value=f"=B{newregs}*{I['Доля дошедших до нужного уровня']}")
c.number_format = '0.0'
c.fill = FILL_OUT
refs = r
r += 1
ws2.cell(row=r, column=1, value="Бонусов за рефералов (700 за каждого)")
c = ws2.cell(row=r, column=2, value=f"=B{refs}*{I['Бонусов Фогейма за 1 реферала']}")
c.number_format = NUM
c.fill = FILL_OUT
ref_bonus = r
r += 1
ws2.cell(row=r, column=1, value="Бонусов за ранг в месяц (лимит по рангу)")
c = ws2.cell(row=r, column=2, value=f"={I['Бонусов Фогейма за ранг в месяц']}")
c.number_format = NUM
c.fill = FILL_OUT
rank_bonus = r
r += 1
ws2.cell(row=r, column=1, value="ИТОГО бонусов Фогейма за месяц (1 бонус = 1 ₽ в магазине)").font = BOLD
c = ws2.cell(row=r, column=2, value=f"=B{ref_bonus}+B{rank_bonus}")
c.font = BOLD
c.number_format = NUM
c.fill = PatternFill("solid", fgColor="FFE699")
r += 1
ws2.cell(row=r, column=3, value="Вывести деньгами нельзя: только оплата Прав, премиума, предметов в магазине Фогейма").font = SMALL
ws2.cell(row=r, column=3).alignment = WRAP
r += 2
ws2.cell(row=r, column=1, value="Суммарный эффект месяца (кэш + игровая ценность)").font = BOLD
c = ws2.cell(row=r, column=2, value=f"=B{net}+B{rank_bonus}+B{ref_bonus}")
c.font = BOLD
c.number_format = MONEY
c.fill = PatternFill("solid", fgColor="DDEBF7")
ws2.freeze_panes = "A3"

# ============================================================ ЛИСТ 3: ПРОГНОЗ 12 МЕС
ws3 = wb.create_sheet("Прогноз 12 мес")
widths(ws3, [10, 14, 14, 14, 14, 16, 16, 16, 16, 14])
title(ws3, "ПРОГНОЗ НА 12 МЕСЯЦЕВ — меняй темп роста, остальное пересчитается", 10)
ws3["A2"] = ("Модель: каждый месяц аудитория и просмотры растут на заданный %. "
             "Доход рассчитывается по тем же формулам, что и на листе «Расчёт месяца».")
ws3["A2"].font = SMALL

head(ws3, 4, ["Месяц", "TG подписчики", "Охват поста TG", "Интеграций", "Просмотры Rutube",
              "Просмотры VK Видео", "Просмотры Дзен", "Рефералов", "Кэш чистыми", "Бонусы Фогейма"])

r5 = 5  # строка параметров роста
ws3.cell(row=5, column=1, value="Темп роста/мес").font = BOLD
growth_cells = {}
for col, val in zip(range(2, 9), [0.35, 0.30, 0.30, 0.45, 0.40, 0.40, 0.30]):
    c = ws3.cell(row=5, column=col, value=val)
    c.fill = FILL_IN
    c.number_format = '0%'
    c.border = BOX
    growth_cells[col] = get_column_letter(col)
ws3.cell(row=5, column=9, value="← редактируй").font = SMALL

START = 6
base = {
    2: f"={I['Подписчиков в Telegram']}",
    3: f"={I['Средний охват одного поста']}",
    4: f"={I['Продажных интеграций в месяц']}",
    5: f"={I['Rutube: просмотров в месяц']}",
    6: f"={I['VK Видео: просмотров в месяц']}",
    7: f"={I['Дзен: просмотров статей в месяц']}",
}
for m in range(12):
    row = START + m
    ws3.cell(row=row, column=1, value=f"Мес {m+1}").font = BOLD
    for col in range(2, 8):
        if m == 0:
            f = base[col]
        else:
            L = get_column_letter(col)
            g = f"{L}$5"
            f = f"={L}{row-1}*(1+{g})"
        c = ws3.cell(row=row, column=col, value=f)
        c.number_format = NUM
        c.border = BOX
    # рефералы: охват контента растёт вместе с аудиторией; берём YouTube как прокси + TG охват
    if m == 0:
        frel = (f"=({I['Охват всего контента за месяц (просмотры)']}*"
                f"{I['CTR на реферальную ссылку']}*"
                f"{I['Конверсия перехода в регистрацию']}*"
                f"{I['Доля новых/вернувшихся среди регистраций']}*"
                f"{I['Доля дошедших до нужного уровня']})")
    else:
        frel = f"=H{row-1}*(1+$H$5)"
    c = ws3.cell(row=row, column=8, value=frel)
    c.number_format = '0.0'
    c.border = BOX
    # кэш чистыми
    cash = (f"=(C{row}/1000*{I['CPM ниши (₽ за 1000 просмотров поста)']}*D{row}"
            f"+E{row}/1000*{I['Rutube: ставка ₽ / 1000 просмотров']}"
            f"+F{row}/1000*{I['VK Видео: ставка ₽ / 1000 просмотров']}"
            f"+G{row}*{I['Доля дочитываний']}*{I['Средняя длительность дочитывания, мин']}*{I['Ставка ₽ за минуту дочитывания']}"
            f"+{I['Boosty/клуб: платящих подписчиков']}*{I['Средний чек подписки, ₽/мес']}"
            f"+{I['Инфопродукты и консультации: продаж в месяц']}*{I['Средний чек продукта, ₽']})"
            f"*(1-{I['Ставка НПД (самозанятый)']})")
    c = ws3.cell(row=row, column=9, value=cash)
    c.number_format = MONEY
    c.fill = FILL_OUT
    c.border = BOX
    # бонусы Фогейма: рефералы × 700 + лимит ранга (упрощённо: берём ввод)
    c = ws3.cell(row=row, column=10,
                 value=f"=H{row}*{I['Бонусов Фогейма за 1 реферала']}+{I['Бонусов Фогейма за ранг в месяц']}")
    c.number_format = NUM
    c.fill = PatternFill("solid", fgColor="FFF2CC")
    c.border = BOX

tot = START + 12
ws3.cell(row=tot, column=1, value="ИТОГО за 12 мес").font = BOLD
c = ws3.cell(row=tot, column=9, value=f"=SUM(I{START}:I{START+11})")
c.font = BOLD
c.number_format = MONEY
c.fill = PatternFill("solid", fgColor="C6E0B4")
c = ws3.cell(row=tot, column=10, value=f"=SUM(J{START}:J{START+11})")
c.font = BOLD
c.number_format = NUM
c.fill = PatternFill("solid", fgColor="FFE699")
ws3.cell(row=tot + 2, column=1,
         value="Это модель, а не обещание. Ключевой драйвер — регулярность публикаций и скорость реакции на патчи.").font = SMALL
ws3.freeze_panes = "B6"

# ============================================================ ЛИСТ 4: ПОРОГИ
ws4 = wb.create_sheet("Пороги и ставки")
widths(ws4, [22, 46, 34, 30])
title(ws4, "ПОРОГИ ПОДКЛЮЧЕНИЯ МОНЕТИЗАЦИИ И ПАРТНЁРКИ", 4)
head(ws4, 2, ["Площадка / программа", "Порог подключения", "Формула / ставка", "Комментарий"])

data = [
    ("Партнёрка Фогейма (вход, L2)", "18+; от 4000 просмотров ИЛИ 4 публикации на Twitch/YouTube за месяц; >50% материалов про игру; нет фрода и нарушения АП",
     "Бонусы, промокоды, премиум, PTS", "Заявка: ru.4game.com/partners/ ; рассматривают в начале месяца; куратор пишет в Telegram"),
    ("Партнёрка: Telegram-шкала", "D: 350 подп. / охват 500. C: 500 / 750. B: 1000 / 1000. A: 2500 / 1500. S: 5000 / 3000",
     "700 бонусов за реферала + до 70 000 бонусов/мес", "Показатели TG не суммируются с YouTube/Twitch"),
    ("Партнёрка: учёт контента", "Видео ≥3 минут; стрим ≥2 часов вживую; AFK-эфиры не засчитываются",
     "Ранги A и S — за рефералов (14 и 25)", "Проверка накруток: Social Blade, TwitchTracker, TGstat"),
    ("Дзен", "30 часов просмотра от подписчиков за последние 30 дней", "~0,05 ₽ за минуту дочитывания", "100 000 просмотров/мес ≈ 4 000–12 000 ₽"),
    ("Rutube", "Самозанятый/ИП/юрлицо + 2 видео + 5000 просмотров", "50–90 ₽ / 1000 просмотров + донаты", "Самый быстрый кэш с видео в РФ"),
    ("VK Видео", "Открытое сообщество ≥3 мес, 5000 подписчиков, охваты ≥30% (или рост +1250/мес)", "50–80% дохода от рекламы; 30–50 ₽ / 1000 просмотров", "Монетизируются только сообщества, не личные страницы; Клипы не монетизируются"),
    ("YouTube", "Монетизация AdSense для авторов из РФ отключена", "0 ₽", "Замедление/ограничения доступа; использовать для охвата и входа в партнёрку"),
    ("Telegram Ads", "Публичный канал, 1000+ подписчиков", "50% дохода от показов, выплаты в TON", "В РФ есть ограничения на вывод — проверяй актуальные условия"),
    ("Telegram: продажа постов", "Практически с 500–1000 подписчиков", "охват/1000 × CPM (100–300 ₽ в игровой нише)", "Обязательна маркировка рекламы через ОРД"),
    ("Boosty / платный канал", "1000+ лояльных подписчиков", "1–3% аудитории × 150–500 ₽/мес", "Прикладная польза, иначе отписки"),
    ("РСЯ / программа Яндекса", "Сайт с трафиком (ориентир 500+ визитов/сут)", "за показы/клики и интеграции товаров", "Подключать на 4–5 месяце, когда есть сайт"),
    ("Другие игры Фогейма", "BNS NEO: от 100 просмотров/мес; Point Blank и «Берсерк»: от 300; Aion/Aion Classic: от 1000",
     "Те же бонусы, отдельные условия", "«Берсерк» учитывает и Rutube. Самый лёгкий вход — BNS NEO"),
    ("Маркировка рекламы", "Обязательна для любой рекламы в интернете (ст. 18.1 ФЗ «О рекламе»)",
     "erid через ОРД + пометка «Реклама» + сведения о рекламодателе", "Штрафы: физлица 2 000–100 000 ₽, юрлица 100 000–500 000 ₽"),
    ("НПД (самозанятость)", "Оформляется бесплатно в «Мой налог»", "4% с физлиц / 6% с юрлиц; лимит 2,4 млн ₽/год", "Без неё Rutube-монетизация недоступна"),
]
r = 3
for row in data:
    for i, v in enumerate(row, start=1):
        c = ws4.cell(row=r, column=i, value=v)
        c.alignment = WRAP
        c.border = BOX
        if i == 1:
            c.font = BOLD
    if r % 2 == 0:
        for i in range(1, 5):
            ws4.cell(row=r, column=i).fill = FILL_GREY
    ws4.row_dimensions[r].height = 46
    r += 1
ws4.freeze_panes = "A3"

# ============================================================ ЛИСТ 5: ПРАЙС
ws5 = wb.create_sheet("Прайс интеграций")
widths(ws5, [18, 20, 20, 20, 44])
title(ws5, "ПРАЙС-ЛИСТ ДЛЯ РЕКЛАМОДАТЕЛЕЙ (считается от твоего охвата)", 5)
head(ws5, 2, ["Охват поста", "Пост 1/24 (низ рынка)", "Пост 1/24 (верх рынка)", "Нативка (+40%)", "Комментарий"])
ws5["A3"] = "CPM низ"
ws5["B3"] = 100
ws5["C3"] = "CPM верх"
ws5["D3"] = 300
for cell in ("B3", "D3"):
    ws5[cell].fill = FILL_IN
    ws5[cell].number_format = MONEY
ws5["A3"].font = SMALL
ws5["C3"].font = SMALL
head(ws5, 5, ["Охват поста", "Пост 1/24 (низ)", "Пост 1/24 (верх)", "Нативная интеграция", "Пакет 3 поста"])
for i, reach in enumerate([500, 1000, 2000, 3000, 5000, 10000, 20000]):
    row = 6 + i
    ws5.cell(row=row, column=1, value=reach).number_format = NUM
    ws5.cell(row=row, column=2, value=f"=A{row}/1000*$B$3").number_format = MONEY
    ws5.cell(row=row, column=3, value=f"=A{row}/1000*$D$3").number_format = MONEY
    ws5.cell(row=row, column=4, value=f"=A{row}/1000*(($B$3+$D$3)/2)*1.4").number_format = MONEY
    ws5.cell(row=row, column=5, value=f"=A{row}/1000*(($B$3+$D$3)/2)*2.6").number_format = MONEY
    for col in range(1, 6):
        ws5.cell(row=row, column=col).border = BOX
ws5.cell(row=14, column=1, value=("Мой текущий охват: подставь значение из листа «Ввод» и смотри строку выше. "
                                  "Формат 1/24 = пост удаляется через сутки, 1/48 = через двое (скидка 20–30%).")).font = SMALL
ws5.merge_cells("A14:E15")
ws5["A14"].alignment = WRAP
ws5.cell(row=17, column=1, value="Обязательная строка маркировки в каждом рекламном посте:").font = BOLD
ws5.cell(row=18, column=1, value="Реклама. {Наименование рекламодателя, ИНН}. erid: {токен ОРД}").font = Font(italic=True)
ws5.merge_cells("A18:E18")

wb.save(OUT)
print("Сохранено:", OUT)
