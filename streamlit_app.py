import os
import streamlit as st
import google.generativeai as genai



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

    def generate_email(self, prompt_data):
        """
        Generate email content based on the structured prompt.
        """
        prompt_template = """Compose an email with the following characteristics:

        *   **Purpose:** {purpose}
        *   **Recipient:** {recipient_info}
        *   **Sender:** {sender_name}
        *   **Tone:** {tone}
        *   **Subject:** {subject}
        *   **Key Points/Content:**
            {key_points}
        *   **Optional Considerations (when applicable):**
            *   **Context:** {context}
            *   **Actions Required:** {actions}
            *   **Attachments:** {attachments}
            *   **Desired Length:** {length}

        Write the email including this information, with an appropriate greeting and closing, considering the desired tone. 
        """

        final_prompt = prompt_template.format(**prompt_data)

        chat = self.model.start_chat(history=[]) #start new session
        try:
           response = chat.send_message(final_prompt)
           if response.candidates and response.candidates[0].finish_reason == "RECITATION":
               print("RECITATION STOPPED")
               return None  # Indicate failure, you may want to retry here.
           else:
               return response.text
        except genai.types.generation_types.StopCandidateException as e:
           print(f"Error: {e}")
           return None # Indicate failure
        
    def paraphrase_text(self, text, tone="neutral"):
        """
        Paraphrase the given text with a specified tone.
        """
        response = self.model.start_chat(history=[]).send_message(
            f"Paraphrase the following text with a '{tone}' tone and return it in Markdown format:\n\n{text}"
        )
        return response.text


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
        page_title="Email Writer & Paraphraser",
        page_icon="✉️",
        layout="wide",
    )

    # Title
    st.title("✉️ Email Writer & Paraphraser 🛠️")
    st.markdown("Create professional emails or paraphrase text with the help of Gemini AI.")
    

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
        st.markdown("Please provide the following details for your email:")
         # Input fields for the structured prompt
        purpose = st.text_input("Purpose", placeholder="e.g. Schedule a meeting")
        recipient_info = st.text_input("Recipient", placeholder="e.g. John Doe, john@example.com")
        sender_name = st.text_input("Sender name", placeholder="e.g. Jane Doe")
        tone = st.text_input("Tone", placeholder="e.g. professional and polite")
        subject = st.text_input("Subject", placeholder="e.g. Meeting Request")
        key_points = st.text_area("Key points (each on a new line)", placeholder="e.g. \n - Confirm availability \n - Discuss the project \n - Assign tasks")
        context = st.text_input("Context (Optional)", placeholder="Background information")
        actions = st.text_input("Actions (Optional)", placeholder="e.g. Please confirm by...")
        attachments = st.text_input("Attachments (Optional)", placeholder="e.g. file1.pdf, file2.docx")
        length = st.text_input("Desired Length (Optional)", placeholder="short, medium, or long")

        if st.button("Generate Email"):
            if any([purpose.strip(), recipient_info.strip(), sender_name.strip(), tone.strip(), subject.strip(), key_points.strip()]):
                prompt_data = {
                    "purpose": purpose,
                    "recipient_info": recipient_info,
                    "sender_name": sender_name,
                    "tone": tone,
                    "subject": subject,
                    "key_points": key_points,
                    "context": context,
                    "actions": actions,
                    "attachments": attachments,
                    "length": length,
                }
                with st.spinner("Generating email..."):
                   email_content = gemini_interface.generate_email(prompt_data)
                if email_content:
                     st.markdown("### Generated Email")
                     st.markdown(email_content, unsafe_allow_html=True)
                     render_download_button(email_content, "generated_email.md", "text/markdown")
                else:
                   st.error("Email generation failed due to recitation issues or an error. Please adjust the prompts.")

            else:
                st.warning("Please provide required details for the email (Purpose, Recipient, Sender, Tone, Subject, and Key Points).")

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
            else:
                st.warning("Please enter text to paraphrase.")


if __name__ == "__main__":
    main()
