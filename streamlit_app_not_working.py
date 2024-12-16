import os
import streamlit as st
import google.generativeai as genai


class GeminiInterface:
    def __init__(self, api_key):
        # Configure Gemini AI
        genai.configure(api_key=api_key)
        self.chat_session = None
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

    def start_chat(self, system_instruction):
        """
        Start a chat session with the given system instruction.
        """
        self.chat_session = genai.start_chat(
            model="gemini-2.0-flash-exp",
            system_message=system_instruction,
            **self.generation_config,
        )

    def chat_message(self, user_message):
        """
        Send a user message to the chat and return the assistant's response.
        """
        if not self.chat_session:
            raise ValueError("Chat session has not been started.")
        response = self.chat_session.send_message(user_message)
        return response["content"]

    def generate_email(self, email_prompt):
        """
        Generate an email using the chat session.
        """
        system_instruction = (
            "You are an expert email writer. Create professional, concise, and well-structured emails."
        )
        if not self.chat_session:
            self.start_chat(system_instruction)
        return self.chat_message(email_prompt)

    def paraphrase_text(self, text, tone):
        """
        Paraphrase text with a specific tone using the chat session.
        """
        system_instruction = (
            f"You are an expert paraphraser. Paraphrase the given text in a {tone} tone."
        )
        if not self.chat_session:
            self.start_chat(system_instruction)
        return self.chat_message(text)


def render_download_button(content, filename, mime_type):
    """
    Render a button to download generated content.
    """
    st.download_button(
        label="📥 Download",
        data=content,
        file_name=filename,
        mime=mime_type,
    )


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Email Generator & Paraphraser",
        page_icon="📧",
        layout="wide",
    )

    # Sidebar Header
    st.sidebar.header("Configuration")
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        st.sidebar.error("API key not found in environment variables!")
        return

    # Initialize GeminiInterface
    if "gemini_interface" not in st.session_state:
        st.session_state.gemini_interface = GeminiInterface(api_key)

    gemini_interface = st.session_state.gemini_interface

    # Tabs for Email Generator and Paraphraser
    tab1, tab2 = st.tabs(["📧 Email Generator", "🔄 Paraphraser"])

    with tab1:
        st.subheader("📧 Email Generator")
        email_prompt = st.text_area(
            "Enter your email prompt",
            placeholder="Provide details about the email you want to generate.",
            key="email_prompt",
        )

        if st.button("Generate Email"):
            if email_prompt.strip():
                with st.spinner("Generating email..."):
                    email_content = gemini_interface.generate_email(email_prompt)
                st.markdown("### Generated Email")
                # Render using `st.chat_message` (includes built-in copy button)
                with st.chat_message("assistant"):
                    st.write(email_content)

                render_download_button(email_content, "generated_email.md", "text/markdown")
            else:
                st.warning("Please provide a valid email prompt.")

    with tab2:
        st.subheader("🔄 Paraphraser")
        text_to_paraphrase = st.text_area(
            "Enter text to paraphrase",
            placeholder="Paste or type the text you want paraphrased.",
            key="paraphrase_text",
        )

        # Tone selection
        tones = ["neutral", "fluent", "academic", "natural", "formal", "simple", "creative", "expand", "shorten"]
        tone = st.selectbox("Select tone", tones, index=0, key="tone_selector")

        custom_tone = st.text_input("Custom tone (optional)", placeholder="E.g., persuasive, friendly")

        # Final tone to use
        selected_tone = custom_tone.strip() if custom_tone.strip() else tone

        if st.button("Paraphrase Text"):
            if text_to_paraphrase.strip():
                with st.spinner(f"Paraphrasing text with a '{selected_tone}' tone..."):
                    paraphrased_text = gemini_interface.paraphrase_text(text_to_paraphrase, selected_tone)
                st.markdown("### Paraphrased Text")
                # Render using `st.chat_message` (includes built-in copy button)
                with st.chat_message("assistant"):
                    st.write(paraphrased_text)

                render_download_button(paraphrased_text, "paraphrased_text.md", "text/markdown")
            else:
                st.warning("Please provide text to paraphrase.")


if __name__ == "__main__":
    main()
