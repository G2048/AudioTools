import time
import gradio as gr

from collections import OrderedDict
from dataclasses import dataclass

from fastapi import FastAPI

PROMPTS = OrderedDict(
    {
        "prompt1": [12, "Оригинальность продукта; Качество/брак;"],
        "prompt2": [46, "text of prompt2"],
        "prompt3": [1000, "text of prompt3"],
        "prompt4": [-2000, "text of prompt4"],
    }
)


def filter_prompts():
    global PROMPTS
    PROMPTS = OrderedDict(filter(lambda items: items[1][0] > 0, PROMPTS.items()))


@dataclass
class TextTitles:
    tokens_balance = '## <span style="color:orange"> Остаток Токенов: %s</span>'
    text_prompt = "## Переменные промпта:\n ```\n%s\n\n```"
    issues = "## Задача: \n ```\n%s\n\n```"
    open_class = '### <span style="color:cyan"> Имя открытого класса: %s </span>'


def do_prompt(name_prompt):
    prompt = PROMPTS[name_prompt]

    start = time.time()
    progress = gr.Progress()
    progress(0, desc="Starting")
    # time.sleep(1)
    progress(0.05)
    len_job = ["one", "two"]
    for progress in progress.tqdm(len_job, desc="Processing"):
        print(progress)
        time.sleep(0.25)

    spent_tokens = int(prompt[0]) - 11
    # Refresh amount of tokens
    prompt[0] = spent_tokens
    filter_prompts()
    # prompt_choises = tuple(PROMPTS.keys())

    execution_time = round(time.time() - start, 2)
    return (
        f"{execution_time} сек.",
        f"{prompt[0]}%",
        f"{spent_tokens}",
        gr.Markdown(TextTitles.tokens_balance % prompt[0]),
    )


def get_text_tokens(name_prompt):
    tokens = PROMPTS[name_prompt][0]
    text = PROMPTS[name_prompt][1]
    return (
        gr.Markdown(TextTitles.tokens_balance % tokens),
        gr.Markdown(TextTitles.text_prompt % text),
    )


def rs_change(rs):
    return gr.update(choices=tuple(PROMPTS.keys()), value=None)


themes = {
    "Base": gr.themes.Base(),
    "Monochrome": gr.themes.Monochrome(),
    "Soft": gr.themes.Soft(),
    "Ocean": gr.themes.Ocean(),
    "Citrus": gr.themes.Citrus(),
    "Glass": gr.themes.Glass(),
}
theme = gr.themes.Ocean(
    primary_hue="fuchsia",
    neutral_hue="indigo",
)
# theme.set(
# primary_hue="indigo",
# secondary_hue="blue",
# neutral_hue="slate",
# font="system",
# )


POPED_THEMES = {}


def del_theme(theme):
    if theme in themes:
        POPED_THEMES[theme] = themes.pop(theme)
    return gr.update(choices=tuple(themes.keys()))


def add_theme(theme):
    themes[theme] = POPED_THEMES[theme]
    return gr.update(choices=themes.keys())


def refresh(theme):
    del_theme(theme)
    return gr.Dropdown(
        choices=tuple(themes.keys()),
        multiselect=False,
        label="Тема",
    )


def get_app(theme):
    with gr.Blocks(
        theme=theme,
        head="Prompts",
        title="Prompts",
        css="footer {visibility: hidden}",
    ) as app:
        # Only show prompts with tokens
        filter_prompts()
        prompt_choises = tuple(PROMPTS.keys())
        first_element = PROMPTS[prompt_choises[0]][0]
        first_text = PROMPTS[prompt_choises[0]][1]
        open_class = "ПРОЧИЕ"

        gr.Markdown("# Prompts")
        mrk_tokens = gr.Markdown(TextTitles.tokens_balance % first_element)
        gr.Markdown("## Themes")
        box_themes = gr.Dropdown(
            choices=themes.keys(),
            multiselect=False,
            label="Тема",
            interactive=True,
        )
        add_themes = gr.Dropdown(
            choices=POPED_THEMES.keys(),
            multiselect=False,
            label="Вернуть Тему",
            interactive=True,
        )
        add_themes.blur(
            fn=lambda x: gr.update(choices=POPED_THEMES.keys()),
            inputs=add_themes,
            outputs=add_themes,
        )
        add_themes.select(
            fn=add_theme,
            inputs=add_themes,
            outputs=box_themes,
        )
        # box_themes.select(
        #     fn=lambda x: themes[x],
        #     inputs=box_themes,
        #     # outputs=get_app(themes),
        # )
        box_themes.select(
            fn=del_theme,
            inputs=box_themes,
            outputs=(box_themes),
        )
        # box_themes.change(
        #     fn=update_themes,
        #     inputs=box_themes,
        #     outputs=box_themes,
        # )

        box_prompt = gr.Dropdown(
            choices=prompt_choises,
            multiselect=False,
            label="Исследование",
            info="Выберите исследование",
        )

        gr.Markdown(TextTitles.issues % "Текст задачи")
        mrk_text_prompt = gr.Markdown(TextTitles.text_prompt % first_text)

        gr.Markdown(TextTitles.open_class % open_class)
        # Change count of tokens and variables of prompts
        box_prompt.select(
            fn=get_text_tokens,
            inputs=box_prompt,
            outputs=(mrk_tokens, mrk_text_prompt),
        )
        text_prompt = gr.Textbox(lines=4, label="Введите свой промпт:")

        button = gr.Button("Отправить промпт!", variant="primary")
        gr.Markdown("#### Результат: ")
        with gr.Row(variant="panel"):
            result_prompts = [
                gr.Textbox(
                    lines=1,
                    interactive=False,
                    label="Время выполнения:",
                    show_copy_button=True,
                ),
                gr.Textbox(
                    lines=1,
                    interactive=False,
                    label="Процент правильных распознований:",
                    show_copy_button=True,
                ),
                gr.Textbox(
                    lines=1,
                    interactive=False,
                    label="Количество потраченных токенов:",
                    show_copy_button=True,
                ),
                mrk_tokens,
            ]
        button.click(fn=do_prompt, inputs=box_prompt, outputs=result_prompts)
        # box_prompt.change(
        #     fn=rs_change,
        #     inputs=box_prompt,
        #     outputs=(mrk_tokens, mrk_text_prompt),
        # )
    return app


def set_app(app: FastAPI):
    return gr.mount_gradio_app(app, get_app(theme), path="/")
