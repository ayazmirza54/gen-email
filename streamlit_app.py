import os
import streamlit as st
import google.generativeai as genai


class GeminiEmailParaphraseInterface:
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
            system_instruction=(
                "You are an expert assistant specializing in paraphrasing text in various tones."
                "You adapt to the specified tone (e.g., formal, creative, simple) and output clear, readable content."
                "Responses must be Markdown formatted."
            ),
        )

        # Initialize chat session
        self.chat_session = None

    def start_chat(self):
        """
        Start a new chat session for paraphrasing.
        """
        self.chat_session = self.model.start_chat(history=[])

    def paraphrase_text(self, text, tone="neutral"):
        """
        Paraphrase the given text with a specified tone.

        :param text: Text to paraphrase
        :param tone: Tone for paraphrasing
        :return: Paraphrased text (Markdown formatted)
        """
        if not self.chat_session:
            self.start_chat()

        response = self.chat_session.send_message(
            f"Paraphrase the following text with a '{tone}' tone and return it in Markdown format:\n\n{text}"
        )
        return response.text


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Paraphraser App",
        page_icon="🔄",
        layout="wide",
    )

    # Title
    st.title("🔄 Paraphraser App")
    st.markdown("Paraphrase text with customizable tone options using Gemini AI.")

    # Sidebar for API key
    st.sidebar.header("Configuration")

    # Fetch API Key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        st.sidebar.error("API key not found in environment variables! Set GEMINI_API_KEY.")
        return

    # Initialize session state for Gemini interface
    if 'gemini_interface' not in st.session_state:
        st.session_state.gemini_interface = GeminiEmailParaphraseInterface(api_key)

    # Paraphrasing Section
    st.subheader("🔄 Paraphrase Text")
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

    if st.button("Paraphrase"):
        if text_to_paraphrase.strip():
            try:
                with st.spinner(f"Paraphrasing text with a '{selected_tone}' tone..."):
                    paraphrased_content = st.session_state.gemini_interface.paraphrase_text(
                        text_to_paraphrase,
                        tone=selected_tone
                    )
                st.markdown("### Paraphrased Text")
                st.markdown(paraphrased_content, unsafe_allow_html=True)  # Render Markdown

                # Add Download and Copy to Clipboard buttons
                st.download_button(
                    label="📥 Download",
                    data=paraphrased_content,
                    file_name="paraphrased_text.md",
                    mime="text/markdown"
                )

                if st.button("📋 Copy to Clipboard"):
                    st.code(
                        """
                        <script>
                        navigator.clipboard.writeText(arguments[0]);
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.error(f"Error during paraphrasing: {e}")
        else:
            st.warning("Please enter text to paraphrase.")

    # Reset button
    if st.sidebar.button("Reset"):
        st.session_state.gemini_interface = None
        st.rerun()


if __name__ == "__main__":
    main()
