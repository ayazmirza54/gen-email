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
                "You can write professional emails based on user inputs and rephrase text for better readability."
            ),
        )

        # Initialize chat session
        self.chat_session = None

    def start_chat(self):
        """
        Start a new chat session for the assistant.
        """
        # Start a blank chat session
        self.chat_session = self.model.start_chat(history=[])

    def generate_email(self, user_input):
        """
        Generate an email based on user input.

        :param user_input: User's email request
        :return: Generated email
        """
        # Ensure chat session is initialized
        if not self.chat_session:
            self.start_chat()

        # Send the email writing request
        response = self.chat_session.send_message(
            f"Write a professional email based on the following request:\n\n{user_input}"
        )
        return response.text

    def paraphrase_text(self, text):
        """
        Paraphrase the given text.

        :param text: Text to paraphrase
        :return: Paraphrased text
        """
        # Ensure chat session is initialized
        if not self.chat_session:
            self.start_chat()

        # Send the paraphrasing request
        response = self.chat_session.send_message(
            f"Paraphrase the following text for better readability:\n\n{text}"
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

    # Initialize session state for chat history and Gemini interface
    if 'gemini_interface' not in st.session_state:
        st.session_state.gemini_interface = GeminiEmailParaphraseInterface(api_key)

    # Tab layout for Email Writing and Paraphrasing
    tab1, tab2 = st.tabs(["📧 Email Writer", "🔄 Paraphraser"])

    with tab1:
        st.subheader("📧 Email Writer")
        email_request = st.text_area("Describe the email you'd like to write (e.g., 'Write an apology email for a missed deadline.')")

        if st.button("Generate Email"):
            if email_request.strip():
                with st.spinner("Generating email..."):
                    email_content = st.session_state.gemini_interface.generate_email(email_request)
                st.text_area("Generated Email", value=email_content, height=300)
            else:
                st.warning("Please provide a description for the email.")

    with tab2:
        st.subheader("🔄 Paraphraser")
        text_to_paraphrase = st.text_area("Enter text to paraphrase")

        if st.button("Paraphrase"):
            if text_to_paraphrase.strip():
                with st.spinner("Paraphrasing text..."):
                    paraphrased_content = st.session_state.gemini_interface.paraphrase_text(text_to_paraphrase)
                st.text_area("Paraphrased Text", value=paraphrased_content, height=300)
            else:
                st.warning("Please enter text to paraphrase.")

    # Reset button
    if st.sidebar.button("Reset"):
        st.session_state.gemini_interface = None
        st.rerun()


if __name__ == "__main__":
    main()
