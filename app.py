# gui-based streamlit app

import re
from typing import Dict

import streamlit as st

from constants import MINIGAME_NAMES, BUFFS
from models import Save, Minigame
from util import fmt, format_time


def format_camel(camel_case_str: str) -> str:
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', camel_case_str).title()


def format_fields(fields: Dict[str, any],
                  *,
                  sep: str = '\n\n',
                  line_fmt: str = '**{k}:** {v}',
                  raw_keys: bool = False,
                  include_unknowns: bool = False) -> str:
    copy = fields.copy()
    if not include_unknowns:
        for key in fields:
            if key.startswith('unknown'):
                del copy[key]

    lines = list(map(lambda t: line_fmt.format(
        k=t[0] if raw_keys else format_camel(t[0]),
        v=format_time(t[1]) if re.search(r'^time[A-Z]', t[0]) or t[0].startswith('unknownTime') else fmt(t[1])
    ), copy.items()))

    return sep.join(lines)


def format_minigame(name: str, minigame: Minigame, *,
                    sep: str, include_unknowns: bool = False) -> str:
    fields = minigame.fields

    # this is ugly, do better

    match name:
        case 'Garden':
            return sep.join([
                format_fields(fields['general'], sep=sep, include_unknowns=include_unknowns),
                f'**Seeds Unlocked:**',
                '<ul>' + ''.join([
                    f'<li>{seed}</li>' for seed, unlocked in fields['seeds'].items() if unlocked
                ]) + '</ul>'
                f'**Plot:** {fields["plot"]}',  # TODO: make the garden pretty
            ])
        case 'Stock Market':
            general = format_fields(fields['general'], sep=sep, include_unknowns=include_unknowns)
            stocks = format_fields(dict(list(map(
                lambda t: (f'<h3>{t[0]}</h3>', format_fields(t[1].fields, sep=sep, include_unknowns=include_unknowns)),
                fields['stocks'].items()
            ))), sep=sep*2, line_fmt='{k}{v}', raw_keys=True, include_unknowns=include_unknowns)
            return sep.join([
                general,
                f'**Open:** {fields["stockMarketOpen"]}',
                stocks,
            ])
        case 'Pantheon':
            copy = fields.copy()
            copy['chosen'] = '/'.join([str(i) for i in fields['chosen']])
            return format_fields(copy, sep=sep, include_unknowns=include_unknowns)
        case _:
            return format_fields(fields, sep=sep, include_unknowns=include_unknowns)


def box(title: str, body: str) -> None:
    st.markdown(f'<div style="border:0px hidden;border-radius:10px;background-color:#172D43;padding:0 20px 5px;">'
                f'<h2>{title}</h2>\n\n'
                f'{body}'
                f'</div>', unsafe_allow_html=True)


st.set_page_config(page_title='Save Inspector', layout='wide', page_icon='🍪')

st.title('Cookie Clicker Save Inspector')
save_code = st.text_input('Enter save code')

save = None
if save_code:
    save = Save(save_code)

if save is not None:
    with st.sidebar:
        st.title('General Info')
        version = save.blocks[0].version
        general = save.blocks[2].fields

        general_copy = general.copy()

        st.markdown(format_fields(general_copy))

        st.title('Statistics')
        stats = save.blocks[4].fields
        st.markdown(format_fields(stats))

    with st.expander('See decoded, but unparsed data'):
        st.write(save.encode())

    col1, col2, col3 = st.columns(3, gap='large')

    minigames = dict()

    with col1:
        st.header('Buildings')

        buildings = save.blocks[5].buildings
        for name, building in buildings.items():
            if minigame := building.fields['minigame']:
                minigames[MINIGAME_NAMES[name]] = minigame

            copy = building.fields.copy()
            del copy['minigame']

            box(name, format_fields(copy, sep='</br>'))

    with col2:
        st.header('Minigames')

        for name, minigame in minigames.items():
            box(name, format_minigame(name, minigame, sep='</br>'))

    with col3:
        st.header('Other')

        buffs = save.blocks[8].buffs
        for buff in buffs:
            copy = buff.fields.copy()
            id = buff.fields['buffId']
            copy['buffId'] = f'{id} ({BUFFS[id]})'
            box('Buff', format_fields(copy, sep='</br>'))

        achievements = save.blocks[7].unlocked
        box('Achievements', '<ul>' + ''.join([
            f'<li>{title}</li>' for title in achievements
        ]) + '</ul>')

        st.write('')  # idk WHY it doesn't just add space like EVERY other box

        options = save.blocks[3].options
        box('Options', '<br>'.join([
            f'**{name}:** ' + ('On' if value else 'Off') for name, value in options.items()
        ]))
