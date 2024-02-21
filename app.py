import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import pandas as pd
from tqdm import tqdm
import pandas as pd
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain

# Initialize OpenAI client with your API key
client = OpenAI(api_key=st.secrets['API_KEY'])

add_specific_hyperlinks = """
Your job is to go through the text of a target blog and add in minimal new text/hyperlinks to sources in our blog database that are most similar to the content of the blog in embeddings space.

First, here is the content of the target blog:
{target_blog}

Next, here are some sources from our database that are most semantically similar to the content of the target blog:
{similar_content}

Given the target blog and the similar content, return the updated target blog that includes naturally- and appropriately-placed hyperlinks to as many of these sources as makes sense given the current content of the target blog.
It is acceptable to add sentences or slightly change phrases to make the hyperlinking more natural, but the overarching goal is to preserve the structure of the original content as much as possible while adding in hyperlinks. 
Accordingly, the ideal case is to find existing text (a word or phrase) where we can simply hyperlink to the relevant sources. It is acceptable if this is not possible for certain links. It is also acceptable to discard certain links/sources if it seems like a clear stretch to try to include them.

Do NOT simply add all of the links at the end of the blog. They should be seamlessly and naturally interspersed within the blog.

You do NOT have to invoke the name of the linked blog, simply adding the link in key places should be sufficient.

Formatting requirements: ONLY output the enhanced target blog (kept exactly the same wherever possible) with appropriately placed links, no other commentary or content.

YOUR OUTPUTS:
"""

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

user_blog_content = st.text_area("Paste your blog content here:", height=300)

if submit:
    with st.spinner("Interspersing related blog post links into your text..."):
        # Find top n similar texts
        top_n_content_list = find_top_n_similar_texts(user_blog_content, blog_df, n, content_preview_length)

        chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4-1106-preview', temperature=0.2)
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(add_specific_hyperlinks), llm=chat_model)
        generated_output = chat_chain.run(target_blog=user_blog_content, similar_content=top_n_content_list)

    # Display the generated content
    st.markdown("## Blog post with relevant hyperlinks interspersed")
    st.markdown(generated_output)
