from YOUTUBE import extract_video_id,GetSubtitles,transcript_to_pdf
import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings






embeddings=HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5",model_kwargs={'device':'cpu'},encode_kwargs={'normalize_embeddings':True})
llm=ChatGroq(groq_api_key="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",
             model_name="llama3-70b-8192")
prompt=ChatPromptTemplate.from_template(
"""
Answer the questions based on the provided context and also with the information present in llm.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions:{input}

"""
)
if 'messages' not in st.session_state:
    st.session_state.messages = []
st.title("ChatBot-Youtube")
st.write("This is a chatbot that can answer questions based on the video transcript of youtube video")

video_link=st.text_input("provide the link")
if video_link:
        video_id = extract_video_id(video_link)
        if type(video_id)==str:
            with st.spinner("Transcripting the  youtube link.."):
                subtitles = GetSubtitles(video_id)
                lines=subtitles.splitlines()
                transcript_to_pdf(lines)


                pdf_loader = PyPDFLoader("transcript.pdf")
                pdf_docs=pdf_loader.load()
                text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
                pdf_final_documents=text_splitter.split_documents(pdf_docs)
                pdf_vectors=FAISS.from_documents(pdf_final_documents,embeddings)
                document_chain = create_stuff_documents_chain(llm, prompt)
                pdf_retriever = pdf_vectors.as_retriever()
                pdf_retrieval_chain = create_retrieval_chain(pdf_retriever, document_chain)


            pdf_prompt=st.chat_input("Enter the prompt here")
            if pdf_prompt:
                with st.spinner("generating the response"):
                    st.session_state.messages.append({'role':'user','content':pdf_prompt})
                    response=pdf_retrieval_chain.invoke({"input":pdf_prompt})
                    st.session_state.messages.append({'role':'assistant','content':response['answer']})
            for messages in st.session_state.messages:
                st.chat_message(messages['role']).markdown(messages['content'])
        else:
             st.error("The provided link cannot be Transcripted :(")