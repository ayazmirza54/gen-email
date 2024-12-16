import os
import streamlit as st
import google.generativeai as genai
import pyperclip


class GeminiInterface:
    def __init__(self, api_key, model_name="gemini-2.0-flash-exp"):
        # Configure API
        genai.configure(api_key=api_key)

        # Generation configuration
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        # Create the model with system instruction
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
        )

    def generate_email(self, prompt):
        """
        Generate email content based on the prompt.
        """
        response = self.model.start_chat(history=[]).send_message(
            f"Generate a professional email based on the following prompt:\n\n{prompt}"
        )
        return response.text

    def paraphrase_text(self, text, tone="neutral"):
        """
        Paraphrase the given text with a specified tone.
        """
        response = self.model.start_chat(history=[]).send_message(
            f"Paraphrase the following text with a '{tone}' tone and return it in Markdown format:\n\n{text}"
        )
        return response.text


def render_copy_to_clipboard(content):
    """
    Render a button for copying text to the clipboard using pyperclip.
    """
    if st.button("📋 Copy to Clipboard"):
        try:
            pyperclip.copy(content)
            st.success("Text copied to clipboard!")
        except Exception as e:
            st.error(f"Failed to copy: {e}")


def render_download_button(content, file_name, mime_type="text/plain"):
    """
    Render a download button for content.
    """
    st.download_button(
        label="📥 Download",
        data=content,
        file_name=file_name,
        mime=mime_type,
    )


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Email Generator & Paraphraser App",
        page_icon="📧",
        layout="wide",
    )

    # Fetch API Key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        st.error("API key not found in environment variables! Set GEMINI_API_KEY.")
        return

    # Initialize Gemini Interface
    gemini_interface = GeminiInterface(api_key)

    # Tabs for Email Generator and Paraphraser
    tab1, tab2 = st.tabs(["📧 Email Generator", "🔄 Paraphraser"])

    with tab1:
        st.subheader("📧 Email Generator")
        email_prompt = st.text_area(
            "Enter your email prompt",
            placeholder="Provide details about the email you want to generate (e.g., purpose, tone, audience)...",
        )

        if st.button("Generate Email"):
            if email_prompt.strip():
                with st.spinner("Generating email..."):
                    email_content = gemini_interface.generate_email(email_prompt)
                st.markdown("### Generated Email")
                st.markdown(email_content, unsafe_allow_html=True)
                render_download_button(email_content, "generated_email.md", "text/markdown")
                render_copy_to_clipboard(email_content)
            else:
                st.warning("Please enter a valid email prompt.")

    with tab2:
        st.subheader("🔄 Paraphraser")
        text_to_paraphrase = st.text_area(
            "Enter text to paraphrase",
            placeholder="Paste or type the text you want paraphrased here."
        )

        # Tone selector
        predefined_tones = [
            "neutral", "fluent", "academic", "natural", "formal",
            "simple", "creative", "expand", "shorten"
        ]
        tone = st.selectbox(
            "Select a tone",
            options=predefined_tones,
            index=0,
        )

        custom_tone = st.text_input(
            "Or specify a custom tone",
            placeholder="E.g., persuasive, friendly, assertive"
        )

        # Determine final tone
        selected_tone = custom_tone.strip() if custom_tone.strip() else tone

        if st.button("Paraphrase Text"):
            if text_to_paraphrase.strip():
                with st.spinner(f"Paraphrasing text with a '{selected_tone}' tone..."):
                    paraphrased_content = gemini_interface.paraphrase_text(
                        text_to_paraphrase,
                        tone=selected_tone
                    )
                st.markdown("### Paraphrased Text")
                st.markdown(paraphrased_content, unsafe_allow_html=True)
                render_download_button(paraphrased_content, "paraphrased_text.md", "text/markdown")
                render_copy_to_clipboard(paraphrased_content)
            else:
                st.warning("Please enter text to paraphrase.")


if __name__ == "__main__":
    main()
