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
                "You are an expert assistant specializing in email writing and paraphrasing."
                "You can write professional emails based on user inputs and rephrase text for better readability, "
                "while adapting to the tone provided by the user."
                "Responses should be clear, helpful, and formatted in Markdown."
            ),
        )

        # Initialize chat session
        self.chat_session = None

    def start_chat(self):
        """
        Start a new chat session for the assistant.
        """
        self.chat_session = self.model.start_chat(history=[])

    def generate_email(self, user_input):
        """
        Generate an email based on user input.

        :param user_input: User's email request
        :return: Generated email (Markdown formatted)
        """
        if not self.chat_session:
            self.start_chat()

        response = self.chat_session.send_message(
            f"Write a professional email in Markdown format based on the following request:\n\n{user_input}"
        )
        return response.text

    def paraphrase_text(self, text, tone="neutral"):
        """
        Paraphrase the given text in a specified tone.

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
        page_title="Email Writer & Paraphraser",
        page_icon="✉️",
        layout="wide",
    )

    # Title
    st.title("✉️ Email Writer & Paraphraser 🛠️")
    st.markdown("Create professional emails or paraphrase text with the help of Gemini AI.")

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Fetch API Key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        st.sidebar.error("API key not found in environment variables! Set GEMINI_API_KEY.")
        return

    # Initialize session state for Gemini interface
    if 'gemini_interface' not in st.session_state:
        st.session_state.gemini_interface = GeminiEmailParaphraseInterface(api_key)

    # Tab layout for Email Writing and Paraphrasing
    tab1, tab2 = st.tabs(["📧 Email Writer", "🔄 Paraphraser"])

    with tab1:
        st.subheader("📧 Email Writer")
        email_request = st.text_area(
            "Describe the email you'd like to write",
            placeholder="E.g., Write a follow-up email after a meeting."
        )

        if st.button("Generate Email"):
            if email_request.strip():
                with st.spinner("Generating email..."):
                    email_content = st.session_state.gemini_interface.generate_email(email_request)
                st.markdown("### Generated Email")
                st.markdown(email_content, unsafe_allow_html=True)  # Render Markdown
                st.download_button(
                    "📋 Copy to Clipboard",
                    email_content,
                    file_name="generated_email.md",
                    mime="text/markdown"
                )
            else:
                st.warning("Please provide a description for the email.")

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

        # Use the custom tone if provided, else use the selected predefined tone
        selected_tone = custom_tone.strip() if custom_tone.strip() else tone

        if st.button("Paraphrase"):
            if text_to_paraphrase.strip():
                with st.spinner(f"Paraphrasing text with a '{selected_tone}' tone..."):
                    paraphrased_content = st.session_state.gemini_interface.paraphrase_text(
                        text_to_paraphrase,
                        tone=selected_tone
                    )
                st.markdown("### Paraphrased Text")
                st.markdown(paraphrased_content, unsafe_allow_html=True)  # Render Markdown
                st.download_button(
                    "📋 Copy to Clipboard",
                    paraphrased_content,
                    file_name="paraphrased_text.md",
                    mime="text/markdown"
                )
            else:
                st.warning("Please enter text to paraphrase.")

    # Reset button
    if st.sidebar.button("Reset"):
        st.session_state.gemini_interface = None
        st.rerun()


if __name__ == "__main__":
    main()
