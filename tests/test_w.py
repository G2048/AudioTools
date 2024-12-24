import gradio as gr

choices = {
    "spanish": ["hola", "bien", "gracias"],
    "english": ["hello", "good", "thank you"],
}


def rs_change(c):
    return gr.Dropdown(
        choices=choices[c[0]], interactive=True
    )  # Make it interactive as it is not by default


interface = gr.Blocks()

with interface:
    main = gr.Dropdown(
        choices=list(choices.keys()), multiselect=True, label="Main Dropdown"
    )
    sub = gr.Dropdown(choices=[], multiselect=False, label="Sub Dropdown")

    main.select(fn=rs_change, inputs=main, outputs=sub)

interface.launch()

