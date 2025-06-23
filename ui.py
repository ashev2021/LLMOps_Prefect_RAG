import gradio as gr
from pipeline import rag_pipeline

def ask_question(query, file):
    try:
        file_path = file.name if file else "data.txt"
        answer, context, dist = rag_pipeline(query, file_path)
        return f"Answer: {answer}\n\nContext: {context}\n\nDistance: {dist:.4f}"
    except Exception as e:
        return f"Error: {str(e)}"

iface = gr.Interface(
    fn=ask_question,
    inputs=[
        gr.Textbox(lines=2, placeholder="Ask a question..."),
        gr.File(label="Upload data file (optional)")
    ],
    outputs="text",
    title="RAG Assistant with context-aware!",
    description="Ask a question and get context-aware answers about your doc."
)

if __name__ == "__main__":
    iface.launch()
