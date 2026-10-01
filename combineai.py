import io
import requests
import streamlit as st
from openai import OpenAI
from huggingface_hub import InferenceClient

st.set_page_config(page_title="AI Mastermind Hub",page_icon="🤖",layout="centered")

try:
    GROQ_API_KEY="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"
    HF_API_KEY="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"
except Exception:
    st.error(
        "API keys are missing. Create .streamlit/secrets.toml "
        "and add GROQ_API_KEY and HF_API_KEY."
    )
    st.stop()
groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
hf_client = InferenceClient(
    provider="auto",
    api_key=HF_API_KEY
)
MODEL = "openai/gpt-oss-20b"

IMAGE_MODELS = {
    "SDXL Base": "stabilityai/stable-diffusion-xl-base-1.0"
}

FILTER_API = "https://filters-zeta.vercel.app/api/filter"



if "ai_history" not in st.session_state:
    st.session_state.ai_history = []

if "math_history" not in st.session_state:
    st.session_state.math_history = []



def check_prompt(prompt):
    """
    Send the image prompt to the external safety filter.
    """

    try:
        response = requests.post(
            FILTER_API,
            json={"prompt": prompt},
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return (
            data.get("ok", False),
            data.get("reason", "")
        )

    except Exception as e:
        return False, str(e)


def generate_answer(prompt):
    """
    Generate an answer using Groq.
    """

    system_prompt = """
You are a helpful AI teaching assistant.

Explain concepts clearly and simply.

Use examples when useful.

Structure your answers with headings or bullet points when appropriate.

Adapt the explanation to the user's question and level.
"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=512
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"


SYSTEM_PROMPT = """
You are a math mastermind.

Solve the problem step by step.

Explain the reasoning clearly.

Give the final answer.

Verify the answer if possible.

Adapt the explanation to the requested difficulty level.
"""


def solve_math(problem, level):
    """
    Solve a math problem using Groq.
    """

    prompt = f"""
{SYSTEM_PROMPT}

Difficulty level: {level}

Problem:
{problem}
"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"



st.sidebar.title("🤖 AI Mastermind Hub")

option = st.sidebar.radio(
    "Choose an application:",
    [
        "🤖 AI Teaching Assistant",
        "🧮 Math Mastermind",
        "🖼️ AI Image Generator"
    ]
)



st.title("🤖 AI Mastermind Hub")

st.write(
    "Choose a tool from the sidebar to start learning, "
    "solving problems, or creating images."
)



if option == "🤖 AI Teaching Assistant":

    st.header("🤖 AI Teaching Assistant")

    st.write(
        "Ask questions about different subjects "
        "and get an AI-generated explanation."
    )

    question = st.text_input(
        "Enter your question",
        placeholder="Example: Explain photosynthesis simply."
    )

    if st.button("Ask", type="primary"):

        if question.strip():

            with st.spinner("Generating response..."):

                answer = generate_answer(question)

            st.session_state.ai_history.insert(
                0,
                {
                    "question": question,
                    "answer": answer
                }
            )

        else:
            st.warning("Please enter a question.")


    if st.session_state.ai_history:

        st.markdown("### 📚 Conversation History")

        download_text = ""

        for i, chat in enumerate(
            st.session_state.ai_history,
            1
        ):

            download_text += f"Question {i}:\n"
            download_text += chat["question"] + "\n\n"

            download_text += "Answer:\n"
            download_text += chat["answer"] + "\n"

            download_text += "\n" + "-" * 50 + "\n\n"

            with st.container(border=True):

                st.markdown(f"### Question {i}")

                st.write(chat["question"])

                st.markdown("### Answer")

                st.markdown(chat["answer"])

        st.download_button(
            label="📥 Download Conversation",
            data=download_text,
            file_name="conversation.txt",
            mime="text/plain",
            use_container_width=True
        )

        if st.button(
            "🗑️ Clear Conversation",
            key="clear_ai_history"
        ):

            st.session_state.ai_history = []

            st.rerun()



elif option == "🧮 Math Mastermind":

    st.header("🧮 Math Mastermind")

    st.write(
        "Enter a math problem and get a step-by-step solution."
    )

    problem = st.text_area(
        "Math Problem",
        placeholder=(
            "Example: Solve x² + 5x + 6 = 0"
        ),
        height=120
    )

    level = st.selectbox(
        "Difficulty Level",
        [
            "Basic",
            "Intermediate",
            "Advanced"
        ]
    )

    if st.button(
        "🧮 Solve",
        type="primary"
    ):

        if not problem.strip():

            st.warning("Please enter a math problem.")

        else:

            with st.spinner("Solving..."):

                answer = solve_math(
                    problem,
                    level
                )

            st.session_state.math_history.insert(
                0,
                {
                    "problem": problem,
                    "answer": answer
                }
            )

            st.subheader("📐 Solution")

            st.markdown(answer)


    if st.session_state.math_history:

        st.subheader("📚 Math History")

        for i, item in enumerate(
            st.session_state.math_history,
            1
        ):

            with st.container(border=True):

                st.markdown(
                    f"### Problem {i}"
                )

                st.write(
                    item["problem"]
                )

                st.markdown("### Answer")

                st.markdown(
                    item["answer"]
                )

        if st.button(
            "🗑️ Clear Math History",
            key="clear_math_history"
        ):

            st.session_state.math_history = []

            st.rerun()



elif option == "🖼️ AI Image Generator":

    st.header("🖼️ Safe AI Image Generator")

    st.write(
        "Enter a description, choose an image model, "
        "and generate an image."
    )


    model_name = st.selectbox(
        "🎨 Image Model",
        list(IMAGE_MODELS.keys())
    )

    model = IMAGE_MODELS[model_name]


    prompt = st.text_area(
        "📝 Image Description",
        placeholder=(
            "A beautiful sunset over the mountains..."
        ),
        height=120
    )


    if st.button(
        "🎨 Generate Image",
        type="primary",
        use_container_width=True
    ):

        if not prompt.strip():

            st.warning(
                "Please enter an image description."
            )

            st.stop()

        prompt = prompt.strip()


        with st.spinner("🔍 Checking prompt..."):

            ok, reason = check_prompt(prompt)

        if not ok:

            st.error(
                "⚠️ Prompt blocked: "
                + (
                    reason
                    or "Prompt did not pass the safety check."
                )
            )

            st.stop()
        with st.spinner(
            f"🎨 Generating with {model_name}..."):
            try:
                image = hf_client.text_to_image(prompt=prompt,model=model)
            except Exception as e:
                st.error("❌ Image generation failed.")
                st.code(str(e),language="text")
                st.info(
                    "Try another image model. "
                    "The selected model may not currently "
                    "have an enabled Inference Provider."
                )
                st.stop()

        st.subheader("🖼️ Generated Image")
        st.image(image,use_container_width=True)
        buffer = io.BytesIO()
        image.save(buffer,format="PNG")
        st.download_button(label="📥 Download Image",data=buffer.getvalue(),file_name="ai_image.png",mime="image/png",use_container_width=True)
st.sidebar.divider()
st.sidebar.caption(
    "AI Mastermind Hub • Learning • Mathematics • Images"
)