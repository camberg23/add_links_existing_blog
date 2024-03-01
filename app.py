import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import pandas as pd
from tqdm import tqdm
import pandas as pd
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
import diff_match_patch as dmp_module

from system_messages import *

# Initialize OpenAI client with your API key
client = OpenAI(api_key=st.secrets['API_KEY'])

def highlight_diffs(original_text, modified_text):
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(original_text, modified_text)
    dmp.diff_cleanupSemantic(diffs)
    html_diff = dmp.diff_prettyHtml(diffs)
    return html_diff
    
def get_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(
        model=model,
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding

def find_top_n_similar_texts(input_text, df, n=5, content_preview_length=100):
    # Generate embedding for the input text
    input_embedding = get_embedding(input_text)
    
    # Function to calculate cosine similarity
    def calculate_cosine_similarity(input_embedding, df_embeddings):
        input_embedding_array = np.array(input_embedding).reshape(1, -1)
        df_embeddings_array = np.stack(df_embeddings)
        similarities = cosine_similarity(input_embedding_array, df_embeddings_array)
        return similarities[0]
    
    # Calculate similarities
    content_similarities = calculate_cosine_similarity(input_embedding, df['content_embedding'])
    
    # Find top N indices for content
    top_n_content_indices = np.argsort(content_similarities)[-n:][::-1]
    
    # Retrieve titles, URLs, and content for the top N indices
    top_n_content_titles = df.iloc[top_n_content_indices]['title'].tolist()
    top_n_content_urls = df.iloc[top_n_content_indices]['urls'].tolist()
    top_n_contents = df.iloc[top_n_content_indices]['content'].apply(lambda x: x[:content_preview_length]).tolist()
    
    # Prepare the output list with title, URL, and content
    output_list = []
    for index, (title, url, content) in enumerate(zip(top_n_content_titles, top_n_content_urls, top_n_contents), start=1):
        output_list.append(f"{index}. Title: {title} | URL: {url} | Content Preview: {content}...")
    
    return output_list


st.title('Add in relevant hyperlinks to already written blog')

blog_df = pd.read_pickle('blog_df.pkl')

n = 10
content_preview_length = 500

user_blog_content = st.text_area("Paste your blog content here:", height=500)

submit = st.button('Intersperse links to related Truity blogs')

if submit:
    with st.spinner("Interspersing related blog post links into your text..."):
        # Find top n similar texts
        top_n_content_list = find_top_n_similar_texts(user_blog_content, blog_df, n, content_preview_length)

        chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4-1106-preview', temperature=0.2)
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(add_specific_hyperlinks), llm=chat_model)
        generated_output = chat_chain.run(target_blog=user_blog_content, similar_content=top_n_content_list)
        blog_content = generated_output.split("BLOG:")[1]
    
    # Display the generated content
    with st.expander("Blog post with relevant hyperlinks interspersed"):
        st.components.v1.html(blog_content, height=400, scrolling=True)

    diff_html = highlight_diffs(user_blog_content, blog_content)
    with st.expander("See the specific changes made"):
        st.components.v1.html(diff_html, height=400, scrolling=True)

    st.download_button(label="Download HTML", data=generated_output, file_name="generated_blog.html", mime="text/html")
