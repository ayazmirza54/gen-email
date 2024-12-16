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
                # Render using Gemini's built-in `chat_message` with a Copy Button
                st.chat_message("assistant").write(email_content)

                render_download_button(email_content, "generated_email.md", "text/markdown")
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
                # Render using Gemini's built-in `chat_message` with a Copy Button
                st.chat_message("assistant").write(paraphrased_content)

                render_download_button(paraphrased_content, "paraphrased_text.md", "text/markdown")
            else:
                st.warning("Please enter text to paraphrase.")
