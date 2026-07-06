"""Gradio UI para industrial-manual-assistant.
Diseñada para grabar el GIF de demo: pregunta → respuesta con sección + página.
"""
import gradio as gr
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def query_manual(question: str, k: int = 5):
    if not question.strip():
        return "Enter a question.", ""

    try:
        r = requests.post(f"{API_URL}/query", json={"question": question, "k": k}, timeout=30)
        data = r.json()
        answer = data["answer"]
        sources_md = "\n".join(
            f"- 📄 **{s['source']}**, §{s.get('section', '')} p.{s['page']} — `score: {s['score']:.3f}`"
            for s in data.get("sources", [])
        )
        return answer, sources_md
    except Exception as e:
        return f"Error: {e}", ""


with gr.Blocks(theme=gr.themes.Base(), title="Industrial Manual Assistant") as demo:
    gr.Markdown("# 🏭 Industrial Manual Assistant")
    gr.Markdown(
        "Ask questions about Siemens S7-1200 and Allen-Bradley Micro820 manuals. "
        "Answers include exact section and page references."
    )

    with gr.Row():
        with gr.Column(scale=2):
            question = gr.Textbox(
                label="Question",
                placeholder='e.g. "How to resolve Error F1 on Siemens S7-1200?"',
                lines=2
            )
            submit = gr.Button("Ask", variant="primary")
        with gr.Column(scale=1):
            k_slider = gr.Slider(1, 10, value=5, step=1, label="Chunks to retrieve")

    answer_box = gr.Markdown(label="Answer")
    sources_box = gr.Markdown(label="Sources")

    gr.Examples(
        examples=[
            ["What causes Error F1 on Siemens S7-1200 and how to resolve it?"],
            ["What is the maximum operating temperature of the CPU 1214C?"],
            ["How to configure Modbus TCP communication on Allen-Bradley Micro820?"],
            ["What are the wiring requirements for digital input modules?"],
        ],
        inputs=question
    )

    submit.click(query_manual, inputs=[question, k_slider], outputs=[answer_box, sources_box])
    question.submit(query_manual, inputs=[question, k_slider], outputs=[answer_box, sources_box])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
