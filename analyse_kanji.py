from browser import document, html


def init_page():
    base_choice = html.DIV(
        "Base à utiliser : " + html.INPUT(**{"id": "base_choice", "value": "base.txt"})
    )
    text_area = html.TEXTAREA(
        **{
            "id": "text_area",
            "placeholder": "Insérer le texte ici ...",
            "rows": "20",
            "cols": "80",
        }
    )
    btn_analyze = html.BUTTON(
        "<span>Analyser </span>", **{"id": "btn_analyze", "class": "button"}
    )
    init_flap()
    document <= html.DIV(**{"id": "app"})
    document["app"] <= base_choice
    document["app"] <= text_area
    document["app"] <= html.BR()
    document["app"] <= btn_analyze
    document["app"] <= html.P(**{"id": "result"})
    # event for analyze button
    document["btn_analyze"].bind("click", text_analysis)


def init_flap():
    flap_content = html.P(
        "Ins&eacute;rer le texte &agrave; analyser dans la zone de texte et cliquer sur le bouton"
        " 'Analyser'. Survoler les ent&ecirc;tes du tableau pour mettre en surbrillance les kanas"
        " correspondants."
    )
    license_link = "https://creativecommons.org/licenses/by-nc/4.0/deed.fr"
    flap_content += html.P(
        html.A(
            html.IMG(
                **{
                    "alt": "Licence Creative Commons",
                    "style": {"border-width": 0},
                    "src": "https://i.creativecommons.org/l/by-nc/4.0/88x31.png",
                }
            ),
            **{"rel": "license", "href": license_link},
        )
        + html.BR()
        + html.H6(
            "Cette œuvre est mise à disposition selon les termes de la "
            + html.A(
                "Licence Creative Commons Attribution - Pas d’Utilisation Commerciale 4.0"
                " International",
                **{"rel": "license", "href": license_link},
            )
        )
    )
    flap_content += html.A(
        **{"href": "#volet", "class": "ouvrir", "aria-hidden": "true"}
    )
    flap_content += html.A(
        **{"href": "#volet_clos", "class": "fermer", "aria-hidden": "true"}
    )
    flap = html.DIV(html.DIV(flap_content, **{"id": "volet"}), **{"id": "volet_clos"})
    document <= flap


def read_base():
    file_content = open(f'bases/{document["base_choice"].value}').read()
    contents = file_content.split("\n")
    contents = [i.strip().split(";") for i in contents[1:] if len(i) > 0]
    return contents


def read_jukugo():
    file_content = open("bases/jukugo.txt").read()
    contents = file_content.split("\n")
    contents = [i.strip() for i in contents if len(i) > 0]
    return contents


def base_data():
    kanji, level = range(2)
    contents = read_base()
    base = {i[kanji]: i[level:] for i in contents}
    return base


def get_levels():
    kanji, level = range(2)
    contents = read_base()
    levels = []
    for i in contents:
        if i[level] not in levels:
            levels.append(i[level])

    return levels


def get_info_names():
    kanji, level, info = range(3)
    file_content = open(document["base_choice"].value).read()
    contents = file_content.split("\n")
    info_names = [i.strip() for i in contents[0].split(";") if len(i) > 0]
    return info_names[info:]


def categorie_over(evt):
    levels = get_levels()
    for i, _ in enumerate(levels):
        col_num = f"col{i}"
        cat_objs = document.querySelectorAll(f".{col_num}")
        for elem in cat_objs.values():
            if elem.classList[0] == evt.target.classList[0]:
                elem.classList.add("highlight")
            else:
                elem.classList.add("fade")


def categorie_out(evt):
    levels = get_levels()
    for i, _ in enumerate(levels):
        col_num = f"col{i}"
        cat_objs = document.querySelectorAll(f".{col_num}")
        for elem in cat_objs.values():
            elem.classList.remove("highlight")
            elem.classList.remove("fade")


def info_kanji_over(evt):
    level, info = range(2)
    base = base_data()
    info_names = get_info_names()
    kanji = evt.target.innerText
    k_infos = base[kanji][info:]
    sclass = {"class": "rmargin"}
    document["kanji_info"].clear()
    document["kanji_info"] <= html.SPAN(
        kanji, **{"class": "rmargin", "style": {"font-size": "20px"}}
    )
    for i, info in enumerate(k_infos):
        info = info_names[i]
        document["kanji_info"] <= html.SPAN(
            html.B(f"{info.title()}: ") + k_infos[i], **sclass
        )
    stroke_order_link = html.A()
    stroke_order_link <= html.B("Ordre des traits")
    stroke_order_link.attrs["href"] = f"https://jisho.org/search/{kanji} %23kanji"
    stroke_order_link.attrs["target"] = "_blank"
    document["kanji_info"] <= stroke_order_link


def text_analysis(event):
    (level,) = range(1)
    # clear the DIV result
    document["result"].clear()
    # read and format text
    txt = document["text_area"].value
    chars = [i for i in txt]
    # load kanji data
    base = base_data()
    levels = get_levels()
    # classify text kanjis
    fchars = []
    not_in_base = set()
    in_base = {c: set() for c in levels}
    for c in chars:
        if c in base:
            lvl = base[c][level]
            cat = levels.index(lvl)
            in_base[lvl].add(c)
            char_span = html.SPAN(c)
            char_span.classList.add(f"col{cat}")
            # event for informations
            char_span.onmouseover = info_kanji_over
            fchars.append(char_span)
        else:
            fchars.append(html.SPAN(c) if c != "\n" else html.BR())
            if len(c.strip()) > 0 and 19903 <= ord(c) <= 40879:
                not_in_base.add(c.strip())

    # detect jukugo
    jukugo_base = read_jukugo()
    txt_by_two = ["".join(i) for i in zip(chars, chars[1:])]
    for i, tbt in enumerate(txt_by_two):
        if tbt in jukugo_base:
            fchars[i].classList.add("jkgo")
            fchars[i + 1].classList.add("jkgo")

    # categories
    categories = html.DIV(**{"id": "entete"})
    for i, lvl in enumerate(levels):
        lvl_count = len(in_base[lvl])
        cat_span = html.SPAN(lvl, **{"id": f"cat_{i}", "class": f"col{i}"})
        # events for categories
        cat_span.onmouseover = categorie_over
        cat_span.onmouseout = categorie_out
        categories <= html.DIV(cat_span + f" : {lvl_count}")

    # unclassified
    if len(not_in_base) > 0:
        unclassified = html.DIV(**{"id": "entete"})
        unclassified <= html.DIV(
            html.I(html.U("non classé(s)")) + " : " + ",".join(not_in_base)
        )

    # kanji info
    kanji_info = html.DIV(**{"id": "kanji_info"})

    # table
    table_contents = html.TD(c for c in fchars)
    table_contents <= html.BR() + chr(160)  # add a blanck line at the end
    table = html.DIV(
        html.TABLE(html.TBODY(html.TR(table_contents))), **{"id": "table-scroll"}
    )

    # insert elements in result DIV
    document["result"] <= categories
    if len(not_in_base) > 0:
        document["result"] <= unclassified
    document["result"] <= kanji_info
    document["result"] <= table


init_page()
