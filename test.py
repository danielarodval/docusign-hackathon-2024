# Extract key terms from the agreement
key_terms = extract_key_terms(uploaded_file)

st.write("Key terms extracted from the agreement:")
st.write(key_terms)

st.write("Summary of the agreement:")
summary = summarize_agreement(uploaded_file)
st.write(summary)

question = st.text_input("Ask a question about the agreement:")
if st.button("Get Answer"):
    answer = get_answer(question, key_terms)
    st.write("Answer:", answer)