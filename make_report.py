import os

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = os.path.dirname(os.path.abspath(__file__))
FIGURES = os.path.join(ROOT, "results", "figures")
OUTPUT = os.path.join(ROOT, "otchet.pdf")

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONTS = {
    "TNR": "Times New Roman.ttf",
    "TNR-Bold": "Times New Roman Bold.ttf",
    "TNR-Italic": "Times New Roman Italic.ttf",
    "TNR-BoldItalic": "Times New Roman Bold Italic.ttf",
}

REPO_URL = "https://github.com/sxd993/poisk-chastnix-naborov"

TABLE_ROWS = [
    ["1", "0,064", "261", "74", "170", "17"],
    ["3", "0,025", "55", "36", "19", "0"],
    ["5", "0,012", "28", "25", "3", "0"],
    ["10", "0,006", "7", "7", "0", "0"],
    ["15", "0,005", "5", "5", "0", "0"],
]


def register_fonts():
    for name, filename in FONTS.items():
        path = os.path.join(FONT_DIR, filename)
        pdfmetrics.registerFont(TTFont(name, path))
    registerFontFamily(
        "TNR",
        normal="TNR",
        bold="TNR-Bold",
        italic="TNR-Italic",
        boldItalic="TNR-BoldItalic",
    )


def make_style(name, **overrides):
    params = {
        "fontName": "TNR",
        "fontSize": 14,
        "leading": 21,
        "textColor": colors.black,
    }
    params.update(overrides)
    return ParagraphStyle(name, **params)


def make_styles():
    return {
        "title": make_style(
            "title", fontName="TNR-Bold", alignment=TA_CENTER, spaceAfter=2
        ),
        "heading": make_style(
            "heading", fontName="TNR-Bold", spaceBefore=14, spaceAfter=8, keepWithNext=True
        ),
        "body": make_style("body", alignment=TA_JUSTIFY, firstLineIndent=12.5 * mm),
        "body_noindent": make_style("body_noindent", alignment=TA_JUSTIFY),
        "bullet": make_style(
            "bullet",
            alignment=TA_JUSTIFY,
            leftIndent=12.5 * mm,
            bulletIndent=6 * mm,
            bulletFontName="TNR",
            bulletFontSize=14,
        ),
        "subbullet": make_style(
            "subbullet",
            alignment=TA_JUSTIFY,
            leftIndent=22 * mm,
            bulletIndent=15.5 * mm,
            bulletFontName="TNR",
            bulletFontSize=14,
        ),
        "center": make_style("center", alignment=TA_CENTER),
        "caption": make_style("caption", alignment=TA_CENTER, spaceBefore=6, spaceAfter=14),
        "table_caption": make_style("table_caption", spaceBefore=10, spaceAfter=6),
        "cell": make_style("cell", alignment=TA_CENTER, leading=18),
        "cellh": make_style(
            "cellh", fontName="TNR-Bold", alignment=TA_CENTER, leading=18
        ),
        "code": make_style("code", alignment=TA_CENTER, spaceBefore=4, spaceAfter=4),
    }


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("TNR", 14)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(A4[0] / 2, 12 * mm, str(canvas.getPageNumber()))
    canvas.restoreState()


def build_table(styles):
    header = [
        [
            Paragraph("Порог<br/>поддержки, %", styles["cellh"]),
            Paragraph("Время<br/>работы, с", styles["cellh"]),
            Paragraph("Число частых наборов", styles["cellh"]),
            Paragraph("", styles["cellh"]),
            Paragraph("", styles["cellh"]),
            Paragraph("", styles["cellh"]),
        ],
        [
            Paragraph("", styles["cellh"]),
            Paragraph("", styles["cellh"]),
            Paragraph("всего", styles["cellh"]),
            Paragraph("длины 1", styles["cellh"]),
            Paragraph("длины 2", styles["cellh"]),
            Paragraph("длины 3", styles["cellh"]),
        ],
    ]
    rows = [[Paragraph(value, styles["cell"]) for value in row] for row in TABLE_ROWS]
    table = Table(
        header + rows,
        colWidths=[30 * mm, 28 * mm, 26 * mm, 27 * mm, 27 * mm, 27 * mm],
        hAlign="CENTER",
        repeatRows=2,
    )
    table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (0, 1)),
                ("SPAN", (1, 0), (1, 1)),
                ("SPAN", (2, 0), (5, 0)),
                ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def figure(styles, filename, caption_text, width_mm=150):
    path = os.path.join(FIGURES, filename)
    with PILImage.open(path) as img:
        width, height = img.size
    flow = Image(
        path,
        width=width_mm * mm,
        height=width_mm * mm * height / width,
        hAlign="CENTER",
    )
    return KeepTogether([flow, Paragraph(caption_text, styles["caption"])])


def build_story(styles):
    story = []
    story.append(Paragraph("ОТЧЕТ", styles["title"]))
    story.append(Paragraph("о выполнении задания", styles["title"]))
    story.append(Paragraph("«Поиск частых наборов объектов»", styles["title"]))
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("1. Формулировка задания", styles["heading"]))
    story.append(Paragraph("Задание включает следующие пункты.", styles["body"]))
    story.append(
        Paragraph(
            "1. Разработайте программу, которая выполняет поиск частых наборов "
            "объектов в заданном наборе данных с помощью алгоритма Apriori "
            "(или одной из его модификаций). Список результирующих наборов "
            "должен содержать как наборы, так и значение поддержки для каждого "
            "набора. Параметрами программы являются набор, порог поддержки и "
            "способ упорядочивания результирующего списка наборов (по убыванию "
            "значения поддержки или лексикографическое).",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "2. Проведите эксперименты на наборе данных baskets.csv (сведения "
            "о покупках в супермаркете). В экспериментах варьируйте пороговое "
            "значение поддержки (например: 1%, 3%, 5%, 10%, 15%).",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "3. Выполните визуализацию результатов экспериментов в виде "
            "следующих диаграмм:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "сравнение быстродействия на фиксированном наборе данных при "
            "изменяемом пороге поддержки;",
            styles["bullet"],
            bulletText="-",
        )
    )
    story.append(
        Paragraph(
            "количество частых наборов объектов различной длины на "
            "фиксированном наборе данных при изменяемом пороге поддержки.",
            styles["bullet"],
            bulletText="-",
        )
    )
    story.append(
        Paragraph(
            "4. Подготовьте отчет о выполнении задания и загрузите отчет "
            "в формате PDF в систему. Отчет должен представлять собой связный "
            "и структурированный документ со следующими разделами:",
            styles["body"],
        )
    )
    for item in (
        "формулировка задания;",
        "гиперссылка на каталог репозитория с исходными текстами, наборами "
        "данных и др. сопутствующими материалами;",
        "рисунки с результатами визуализации;",
        "пояснения, раскрывающие смысл полученных результатов.",
    ):
        story.append(Paragraph(item, styles["bullet"], bulletText="-"))

    story.append(Paragraph("2. Исходные тексты и сопутствующие материалы", styles["heading"]))
    story.append(
        Paragraph(
            "Исходные тексты программы, набор данных, результаты экспериментов "
            "и диаграммы размещены в репозитории по адресу:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            '<link href="%s"><u>%s</u></link>' % (REPO_URL, REPO_URL),
            styles["center"],
        )
    )
    story.append(Paragraph("Репозиторий содержит следующие материалы:", styles["body"]))
    for item in (
        "apriori.py, программа поиска частых наборов объектов алгоритмом "
        "Apriori;",
        "experiments.py, модуль проведения экспериментов и построения "
        "диаграмм;",
        "baskets.csv, набор данных о покупках в супермаркете, содержит 7501 "
        "транзакцию;",
        "results, каталог с результатами: списками частых наборов для каждого "
        "значения порога, сводными показателями в файле metrics.json и "
        "диаграммами;",
        "requirements.txt, перечень зависимостей.",
    ):
        story.append(Paragraph(item, styles["bullet"], bulletText="-"))
    story.append(
        Paragraph(
            "Программа apriori.py реализует классическую схему алгоритма "
            "Apriori. На первой итерации подсчитывается поддержка всех "
            "одноэлементных наборов и отбираются частые. Далее на каждой "
            "итерации из частых наборов длины k-1 формируются кандидаты длины "
            "k, отбрасываются кандидаты, у которых хотя бы один поднабор длины "
            "k-1 не является частым, и по всем транзакциям подсчитывается "
            "поддержка оставшихся кандидатов. Итерации продолжаются до тех "
            "пор, пока обнаруживаются новые частые наборы.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Параметрами программы являются путь к набору данных, порог "
            "поддержки и способ упорядочивания результирующего списка. Порог "
            "поддержки задается в одном из форматов: 0.05, 5 или 5%. "
            "Результирующий список упорядочивается по убыванию значения "
            "поддержки (значение support) либо лексикографически (значение "
            "lex). Для каждого найденного набора выводится значение "
            "относительной поддержки. Пример запуска программы:",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "python3 apriori.py --data baskets.csv --min-support 5% --order support",
            styles["code"],
        )
    )

    story.append(Paragraph("3. Результаты экспериментов", styles["heading"]))
    story.append(
        Paragraph(
            "Эксперименты проведены на наборе данных baskets.csv, содержащем "
            "7501 транзакцию. Порог поддержки принимал значения 1%, 3%, 5%, "
            "10% и 15%. Для каждого значения порога измерялись время работы "
            "алгоритма и число найденных частых наборов, в том числе в "
            "разбивке по длине набора. Сводные результаты экспериментов "
            "приведены в таблице 1.",
            styles["body"],
        )
    )
    story.append(
        KeepTogether(
            [
                Paragraph(
                    "Таблица 1. Результаты экспериментов при варьировании "
                    "порога поддержки",
                    styles["table_caption"],
                ),
                build_table(styles),
            ]
        )
    )
    story.append(
        Paragraph(
            "Зависимость времени работы алгоритма от порога поддержки "
            "представлена на рисунке 1. Распределение числа частых наборов "
            "по длинам при различных значениях порога представлено на "
            "рисунке 2.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        figure(
            styles,
            "runtime_vs_support.png",
            "Рисунок 1. Зависимость времени работы алгоритма от порога "
            "поддержки",
        )
    )
    story.append(
        figure(
            styles,
            "itemsets_by_length.png",
            "Рисунок 2. Число частых наборов различной длины при различных "
            "значениях порога поддержки",
        )
    )

    story.append(Paragraph("4. Пояснения к полученным результатам", styles["heading"]))
    story.append(
        Paragraph(
            "Поддержка обладает свойством антимонотонности: любой поднабор "
            "частого набора также является частым, и, следовательно, если "
            "некоторый набор не является частым, то частым не может быть ни "
            "один содержащий его набор. Из этого свойства следует, что с "
            "ростом порога поддержки число частых наборов может только "
            "убывать. В проведенных экспериментах при пороге 1% алгоритм "
            "находит 261 частый набор, а при пороге 15% лишь 5 наборов.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Время работы алгоритма сокращается с 0,064 с при пороге 1% до "
            "0,005 с при пороге 15%, то есть примерно в 13 раз. При низком "
            "пороге частыми признаются многие одноэлементные наборы, из них "
            "строится большое число кандидатов длины 2 и 3, и поддержка "
            "каждого кандидата подсчитывается по всем 7501 транзакциям. При "
            "порогах 10% и 15% частыми остаются только одноэлементные наборы, "
            "построение кандидатов прекращается после первой итерации, и "
            "время работы определяется однократным подсчетом поддержки "
            "отдельных товаров.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Распределение числа частых наборов по длинам отражает тот же "
            "эффект. При пороге 1% найдено 74 набора длины 1, 170 наборов "
            "длины 2 и 17 наборов длины 3, наборы большей длины частыми не "
            "являются. При пороге 3% остаются наборы только длины 1 и 2, их "
            "36 и 19 соответственно. При пороге 5% найдено 25 одноэлементных "
            "наборов и 3 набора длины 2, а при порогах 10% и 15% частыми "
            "являются только одноэлементные наборы, 7 и 5 соответственно.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "С точки зрения предметной области наиболее поддерживаемыми "
            "товарами являются минеральная вода (23,8%), макароны (18,8%), "
            "яйца (18,0%), картофель-фри (17,1%) и шоколад (16,4%). Наиболее "
            "поддерживаемый набор из двух товаров, макароны и минеральная "
            "вода, встречается в 6,1% транзакций, а наиболее поддерживаемый "
            "набор из трех товаров, говяжий фарш, макароны и минеральная "
            "вода, в 1,7% транзакций. Найденные частые наборы служат основой "
            "для построения ассоциативных правил и могут применяться в "
            "практических задачах торговли, например при размещении товаров "
            "в торговом зале и при формировании комплексных предложений на "
            "совместно покупаемые товары.",
            styles["body"],
        )
    )

    story.append(Paragraph("5. Заключение", styles["heading"]))
    story.append(
        Paragraph(
            "В ходе выполнения задания разработана программа поиска частых "
            "наборов объектов алгоритмом Apriori с параметрами: набор данных, "
            "порог поддержки и способ упорядочивания результата. На наборе "
            "данных baskets.csv проведены эксперименты при порогах поддержки "
            "1%, 3%, 5%, 10% и 15%, выполнена визуализация результатов в виде "
            "диаграмм быстродействия и распределения числа частых наборов по "
            "длинам. Полученные результаты согласуются со свойством "
            "антимонотонности поддержки: снижение порога приводит к "
            "существенному росту числа частых наборов и времени работы "
            "алгоритма. Все пункты задания выполнены в полном объеме.",
            styles["body"],
        )
    )
    return story


def main():
    register_fonts()
    styles = make_styles()
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=30 * mm,
        rightMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Отчет о выполнении задания. Поиск частых наборов объектов",
        author="Gurbanovich Vladimir",
    )
    doc.build(
        build_story(styles),
        onFirstPage=page_number,
        onLaterPages=page_number,
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
