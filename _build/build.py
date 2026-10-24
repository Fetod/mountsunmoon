"""Assemble en/, zh-hans/, ja/ pages from the 繁中 index.html head + translated bodies,
and add the language switcher to all four pages. Run from the repo root."""
import re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "index.html").read_text(encoding="utf-8")

LANGS = [  # (code, folder, label)
    ("zh-Hant", "", "繁中"),
    ("zh-Hans", "zh-hans/", "简中"),
    ("en", "en/", "EN"),
    ("ja", "ja/", "日本語"),
]

def switcher(cur, depth):
    up = "../" * depth
    links = []
    for code, folder, label in LANGS:
        href = up + folder if (up + folder) else "./"
        attr = ' aria-current="page"' if code == cur else ""
        links.append(f'<a href="{href}" hreflang="{code}" lang="{code}"{attr}>{label}</a>')
    return '<div class="langs" aria-label="Language">' + "".join(links) + "</div>"

def hreflang():
    out = []
    for code, folder, _ in LANGS:
        out.append(f'<link rel="alternate" hreflang="{code}" href="https://mountsunmoon.com/{folder}">')
    out.append('<link rel="alternate" hreflang="x-default" href="https://mountsunmoon.com/">')
    return "\n".join(out)

SWITCH_CSS = """
/* language switcher */
.langs { display: flex; gap: 2px; font-size: 12px; letter-spacing: 0.06em; flex-shrink: 0; }
.langs a { text-decoration: none; color: var(--mute); padding: 4px 7px; border: 1px solid transparent; }
.langs a:hover, .langs a:focus-visible { color: var(--paper); }
.langs a[aria-current] { color: var(--gold); border-color: var(--line); }
header nav { margin-left: auto; }
@media (max-width: 420px) { .langs a { padding: 4px 5px; } .brand small { display: none; } }
"""

FONTS = {
    "en": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Noto+Sans:wght@300;400;500&family=Noto+Serif+TC:wght@400&display=swap",
    "zh-Hans": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Noto+Sans+SC:wght@300;400;500&family=Noto+Serif+SC:wght@400;600&family=Noto+Serif+TC:wght@400&display=swap",
    "ja": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Noto+Sans+JP:wght@300;400;500&family=Noto+Serif+JP:wght@400;600&family=Noto+Serif+TC:wght@400&display=swap",
}

OVERRIDES = {
    "en": """
:root { --serif: "Cormorant Garamond", "Noto Serif TC", Georgia, serif; --sans: "Noto Sans", "Helvetica Neue", Arial, sans-serif; }
body { letter-spacing: 0.005em; line-height: 1.75; }
h1, h2, h3 { font-weight: 500; }
.hero h1 { letter-spacing: 0.02em; font-size: clamp(28px, 5vw, 50px); line-height: 1.3; }
h2 { font-size: clamp(30px, 4.8vw, 46px); line-height: 1.25; }
.cols h3, .tdp h3 { font-size: 23px; }
.artisan h3 { font-size: 30px; }
.rows { grid-template-columns: 9.5em 1fr; }
.rows dt.theme { white-space: normal; font-size: 17px; }
.rows .verse { font-style: italic; font-size: 18px; }
td:first-child { white-space: normal; min-width: 11em; font-size: 17px; }
.tdp b, .brand b, footer .mark { font-family: "Noto Serif TC", serif; }
.spirit .zh-line { font-family: "Noto Serif TC", serif; }
.spirit p.en { font-size: clamp(20px, 3vw, 28px); }
summary { font-size: 19px; }
.pull { font-size: clamp(22px, 3.4vw, 30px); line-height: 1.5; }
.plan h3 { font-size: 25px; }
.steps b { font-size: 26px; }
""",
    "zh-Hans": """
:root { --serif: "Noto Serif SC", "Songti SC", "SimSun", serif; --sans: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; }
.brand b, .tdp b { font-family: "Noto Serif TC", "Noto Serif SC", serif; }
""",
    "ja": """
:root { --serif: "Noto Serif JP", "Hiragino Mincho ProN", "Yu Mincho", serif; --sans: "Noto Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif; }
.hero h1 { letter-spacing: 0.08em; }
.rows { grid-template-columns: 8.5em 1fr; }
.rows dt.theme { white-space: normal; }
.spirit .zh-line, .brand b { font-family: "Noto Serif TC", serif; }
nav { gap: 16px; font-size: 12.5px; }
@media (max-width: 1080px) { nav { display: none; } }
""",
}

META = {
    "en": ("Mount Sun Moon 日月山",
           "Mount Sun Moon Collector Series Christmas pre-order: five roasters, five fires, one box. 5% of every pre-order supports children's arts and music programmes."),
    "zh-Hans": ("日月山 Mount Sun Moon",
                "日月山 Mount Sun Moon 藏家系列圣诞预购：五位烘豆师、五种火候、一个盒子。每笔预购提拨商品售价 5% 支持孩子的艺术与音乐课程。"),
    "ja": ("日月山 Mount Sun Moon",
           "日月山 Mount Sun Moon コレクターズシリーズ クリスマス予約：五人の焙煎士、五つの火、ひとつの箱。ご予約ごとに商品価格の 5% を子どもたちの芸術・音楽の授業に。"),
}

head_end = src.index("</head>")
head = src[:head_end]
fonts_re = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">')
desc_re = re.compile(r'<meta name="description" content="[^"]*">')

for code, folder, _ in LANGS[1:]:
    h = head.replace('<html lang="zh-Hant">', f'<html lang="{code}">')
    h = fonts_re.sub(f'<link rel="stylesheet" href="{FONTS[code]}">', h)
    title, desc = META[code]
    h = desc_re.sub(f'<meta name="description" content="{desc}">', h)
    h = h.replace("<title>日月山 Mount Sun Moon</title>", f"<title>{title}</title>")
    h = h.replace("</style>", SWITCH_CSS + OVERRIDES[code] + "</style>\n" + hreflang(), 1)
    body = (root / "_build" / f"{folder.strip('/')}.html").read_text(encoding="utf-8")
    body = body.replace("{{LANGS}}", switcher(code, 1))
    out = h + "</head>\n<body>\n" + body + "</body>\n</html>\n"
    (root / folder).mkdir(exist_ok=True)
    (root / folder / "index.html").write_text(out, encoding="utf-8")
    print("wrote", folder + "index.html", len(out))

# 繁中 root page: add switcher + hreflang once (idempotent)
if 'class="langs"' not in src:
    s = src.replace("</style>", SWITCH_CSS + "</style>\n" + hreflang(), 1)
    s = s.replace("    </nav>\n  </div>\n</header>", "    </nav>\n    " + switcher("zh-Hant", 0) + "\n  </div>\n</header>", 1)
    assert 'class="langs"' in s
    (root / "index.html").write_text(s, encoding="utf-8")
    print("updated index.html")
