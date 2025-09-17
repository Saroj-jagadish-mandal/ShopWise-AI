# import streamlit as st
# from scrape import scrape_website

# st.title("AI POWERED WEB ASSISTANT")

# url = st.text_input("Enter a website URL:")
# st.write("Current URL:", url)


# if st.button("Scrape Site"):
#     st.write("Scraping the website...")
#     result=scrape_website(url)
#     print(result)
# import streamlit as st
# import json
# import time
# from datetime import datetime
# import pandas as pd
# from scrape_enhanced import AmazonProductScraper  # Import the enhanced scraper

# # Configure Streamlit page
# st.set_page_config(
#     page_title="AI Powered Web Assistant",
#     page_icon="🤖",
#     layout="wide"
# )

# def scrape_website(url):
#     """Enhanced scraping function compatible with your original structure"""
#     try:
#         chrome_driver_path = r"C:\Users\saroj mandal\OneDrive\Desktop\ai_powered_web_assistant\chromedriver.exe"
#         scraper = AmazonProductScraper(chrome_driver_path)
#         result = scraper.scrape_product_data(url)
#         return result
#     except Exception as e:
#         st.error(f"Error during scraping: {str(e)}")
#         return None

# def display_product_data(data):
#     """Display scraped product data in a user-friendly format"""
#     if not data:
#         st.error("No data to display")
#         return
    
#     # Create tabs for different sections
#     tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Basic Info", "🏷️ Pricing & Details", "📊 Specifications", "🛍️ Additional Info", "📄 Raw Data"])
    
#     with tab1:
#         st.header("📝 Product Basic Information")
        
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             if data.get('title'):
#                 st.subheader("Product Title")
#                 st.write(data['title'])
            
#             if data.get('brand'):
#                 st.subheader("Brand")
#                 st.write(data['brand'])
                
#             if data.get('description'):
#                 st.subheader("Description")
#                 st.write(data['description'])
                
#             if data.get('categories'):
#                 st.subheader("Categories")
#                 st.write(" > ".join(data['categories']))
        
#         with col2:
#             if data.get('images') and len(data['images']) > 0:
#                 st.subheader("Product Images")
#                 for i, img_url in enumerate(data['images'][:3]):  # Show first 3 images
#                     try:
#                         st.image(img_url, caption=f"Image {i+1}", width=200)
#                     except:
#                         st.write(f"Image {i+1}: {img_url}")
    
#     with tab2:
#         st.header("🏷️ Pricing & Customer Feedback")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.subheader("💰 Pricing")
#             if data.get('current_price'):
#                 st.metric("Current Price", data['current_price'])
#             if data.get('original_price'):
#                 st.metric("Original Price", data['original_price'])
#             if data.get('availability'):
#                 st.info(f"Availability: {data['availability']}")
        
#         with col2:
#             st.subheader("⭐ Customer Ratings")
#             if data.get('rating'):
#                 st.metric("Rating", data['rating'])
#             if data.get('review_count'):
#                 st.metric("Reviews", data['review_count'])
#             if data.get('sales_rank'):
#                 st.info(f"Sales Rank: {data['sales_rank']}")
        
#         with col3:
#             st.subheader("🚚 Shipping")
#             if data.get('shipping_info'):
#                 for shipping in data['shipping_info']:
#                     st.write(f"• {shipping}")
    
#     with tab3:
#         st.header("📊 Product Specifications")
        
#         if data.get('specifications'):
#             # Convert specifications to DataFrame for better display
#             spec_df = pd.DataFrame(
#                 list(data['specifications'].items()),
#                 columns=['Specification', 'Value']
#             )
#             st.dataframe(spec_df, use_container_width=True)
#         else:
#             st.info("No specifications available")
        
#         if data.get('variants'):
#             st.subheader("Available Variants")
#             for variant in data['variants']:
#                 st.write(f"• {variant}")
    
#     with tab4:
#         st.header("🛍️ Additional Information")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             if data.get('qa'):
#                 st.subheader("❓ Customer Q&A")
#                 for i, qa in enumerate(data['qa'][:5]):  # Show first 5 Q&As
#                     st.write(f"**Q&A {i+1}:** {qa}")
        
#         with col2:
#             if data.get('related_products'):
#                 st.subheader("🔗 Related Products")
#                 for product in data['related_products'][:5]:  # Show first 5
#                     st.write(f"• [{product['title']}]({product['url']})")
    
#     with tab5:
#         st.header("📄 Raw JSON Data")
#         st.json(data)

# def save_data_locally(data, filename=None):
#     """Save scraped data to local JSON file"""
#     if not filename:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"scraped_data_{timestamp}.json"
    
#     try:
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(data, f, ensure_ascii=False, indent=4)
#         return filename
#     except Exception as e:
#         st.error(f"Error saving file: {str(e)}")
#         return None

# # Main Streamlit App
# def main():
#     st.title("🤖 AI POWERED WEB ASSISTANT")
#     st.markdown("### Amazon Product Data Scraper")
    
#     # URL input
#     url = st.text_input(
#         "Enter an Amazon product URL:",
#         placeholder="https://www.amazon.com/dp/PRODUCT_ID",
#         help="Paste the full Amazon product URL here"
#     )
    
#     st.write("**Current URL:**", url if url else "No URL entered")
    
#     # Validation
#     if url and not ("amazon.com" in url.lower() or "amazon.in" in url.lower()):
#         st.warning("⚠️ This scraper is optimized for Amazon URLs. Other websites may not work properly.")
    
#     col1, col2, col3 = st.columns([1, 1, 2])
    
#     with col1:
#         scrape_button = st.button("🔍 Scrape Product Data", type="primary")
    
#     # Scraping process
#     if scrape_button and url:
#         if not url.strip():
#             st.error("Please enter a valid URL")
#         else:
#             # Progress indicators
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             try:
#                 status_text.text("🚀 Initializing scraper...")
#                 progress_bar.progress(20)
                
#                 status_text.text("🌐 Loading webpage...")
#                 progress_bar.progress(40)
                
#                 status_text.text("📊 Extracting product data...")
#                 progress_bar.progress(60)
                
#                 # Perform scraping
#                 result = scrape_website(url)
                
#                 progress_bar.progress(80)
#                 status_text.text("✅ Processing results...")
                
#                 progress_bar.progress(100)
#                 status_text.text("🎉 Scraping completed!")
                
#                 time.sleep(1)  # Brief pause for user experience
                
#                 # Clear progress indicators
#                 progress_bar.empty()
#                 status_text.empty()
                
#                 if result:
#                     st.success("✅ Product data scraped successfully!")
                    
#                     # Display results
#                     display_product_data(result)
                    
#                     # Download options
#                     st.markdown("---")
#                     st.subheader("💾 Download Options")
                    
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         # JSON download
#                         json_str = json.dumps(result, ensure_ascii=False, indent=4)
#                         st.download_button(
#                             label="📄 Download as JSON",
#                             data=json_str,
#                             file_name=f"product_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                             mime="application/json"
#                         )
                    
#                     with col2:
#                         # CSV download (flattened data)
#                         if result.get('specifications'):
#                             try:
#                                 # Create a simplified CSV with basic info
#                                 csv_data = {
#                                     'Title': [result.get('title', 'N/A')],
#                                     'Brand': [result.get('brand', 'N/A')],
#                                     'Current Price': [result.get('current_price', 'N/A')],
#                                     'Rating': [result.get('rating', 'N/A')],
#                                     'Review Count': [result.get('review_count', 'N/A')],
#                                     'Availability': [result.get('availability', 'N/A')]
#                                 }
#                                 csv_df = pd.DataFrame(csv_data)
#                                 csv_str = csv_df.to_csv(index=False)
                                
#                                 st.download_button(
#                                     label="📊 Download as CSV",
#                                     data=csv_str,
#                                     file_name=f"product_basic_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#                                     mime="text/csv"
#                                 )
#                             except:
#                                 pass
                    
#                     # Store in session state for RAG processing
#                     st.session_state['scraped_data'] = result
#                     st.session_state['last_scraped_url'] = url
                    
#                 else:
#                     st.error("❌ Failed to scrape product data. Please check the URL and try again.")
#                     st.info("💡 Tips:\n- Ensure the URL is a valid Amazon product page\n- Check your internet connection\n- Try with a different product URL")
                    
#             except Exception as e:
#                 progress_bar.empty()
#                 status_text.empty()
#                 st.error(f"❌ An error occurred during scraping: {str(e)}")
    
#     elif scrape_button and not url:
#         st.error("Please enter a URL before scraping")
    
#     # Sidebar with additional info
#     with st.sidebar:
#         st.header("ℹ️ Information")
#         st.info(
#             "This tool scrapes comprehensive product data from Amazon including:\n\n"
#             "• Product details & descriptions\n"
#             "• Pricing information\n"
#             "• Customer ratings & reviews\n"
#             "• Product specifications\n"
#             "• Images & variants\n"
#             "• Related products\n"
#             "• Q&A sections"
#         )
        
#         st.header("🎯 Usage Tips")
#         st.markdown(
#             "1. **Copy the full Amazon product URL**\n"
#             "2. **Paste it in the input field**\n"
#             "3. **Click 'Scrape Product Data'**\n"
#             "4. **View results in organized tabs**\n"
#             "5. **Download data for your RAG system**"
#         )
        
#         if 'scraped_data' in st.session_state:
#             st.header("📈 Session Info")
#             st.success(f"✅ Last scraped: {st.session_state.get('last_scraped_url', 'N/A')}")
            
#             if st.button("🗑️ Clear Session Data"):
#                 if 'scraped_data' in st.session_state:
#                     del st.session_state['scraped_data']
#                 if 'last_scraped_url' in st.session_state:
#                     del st.session_state['last_scraped_url']
#                 st.rerun()

# if __name__ == "__main__":
#     main()

# import streamlit as st
# import json
# import time
# from datetime import datetime
# from scrape_enhanced import AmazonProductScraper  # Import the enhanced scraper

# # Configure Streamlit page
# st.set_page_config(
#     page_title="AI Powered Web Assistant",
#     page_icon="🤖",
#     layout="wide"
# )

# def scrape_website(url):
#     """Enhanced scraping function compatible with your original structure"""
#     try:
#         chrome_driver_path = r"C:\Users\saroj mandal\OneDrive\Desktop\ai_powered_web_assistant\chromedriver.exe"
#         scraper = AmazonProductScraper(chrome_driver_path)
#         result = scraper.scrape_product_data(url)
#         return result
#     except Exception as e:
#         st.error(f"Error during scraping: {str(e)}")
#         return None

# def print_to_terminal(data):
#     """Print the scraped data to the terminal"""
#     try:
#         # Pretty print the JSON data to the terminal
#         print("\n=== Scraped Product Data ===")
#         print(json.dumps(data, ensure_ascii=False, indent=4))
#         print("==========================\n")
#     except Exception as e:
#         print(f"Error printing data to terminal: {str(e)}")

# # Main Streamlit App
# def main():
#     st.title("🤖 AI POWERED WEB ASSISTANT")
#     st.markdown("### Amazon Product Data Scraper")
    
#     # URL input
#     url = st.text_input(
#         "Enter an Amazon product URL:",
#         placeholder="https://www.amazon.com/dp/PRODUCT_ID",
#         help="Paste the full Amazon product URL here"
#     )
    
#     st.write("**Current URL:**", url if url else "No URL entered")
    
#     # Validation
#     if url and not ("amazon.com" in url.lower() or "amazon.in" in url.lower()):
#         st.warning("⚠️ This scraper is optimized for Amazon URLs. Other websites may not work properly.")
    
#     col1, col2, col3 = st.columns([1, 1, 2])
    
#     with col1:
#         scrape_button = st.button("🔍 Scrape Product Data", type="primary")
    
#     # Scraping process
#     if scrape_button and url:
#         if not url.strip():
#             st.error("Please enter a valid URL")
#         else:
#             # Progress indicators
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             try:
#                 status_text.text("🚀 Initializing scraper...")
#                 progress_bar.progress(20)
                
#                 status_text.text("🌐 Loading webpage...")
#                 progress_bar.progress(40)
                
#                 status_text.text("📊 Extracting product data...")
#                 progress_bar.progress(60)
                
#                 # Perform scraping
#                 result = scrape_website(url)
                
#                 progress_bar.progress(80)
#                 status_text.text("✅ Processing results...")
                
#                 progress_bar.progress(100)
#                 status_text.text("🎉 Scraping completed!")
                
#                 time.sleep(1)  # Brief pause for user experience
                
#                 # Clear progress indicators
#                 progress_bar.empty()
#                 status_text.empty()
                
#                 if result:
#                     # Print data to terminal instead of displaying
#                     print_to_terminal(result)
#                     st.success("✅ Data has been fetched and printed to the terminal!")
                    
#                     # Store in session state (optional, for tracking)
#                     st.session_state['last_scraped_url'] = url
                    
#                 else:
#                     st.error("❌ Failed to scrape product data. Please check the URL and try again.")
#                     st.info("💡 Tips:\n- Ensure the URL is a valid Amazon product page\n- Check your internet connection\n- Try with a different product URL")
                    
#             except Exception as e:
#                 progress_bar.empty()
#                 status_text.empty()
#                 st.error(f"❌ An error occurred during scraping: {str(e)}")
    
#     elif scrape_button and not url:
#         st.error("Please enter a URL before scraping")
    
#     # Sidebar with additional info
#     with st.sidebar:
#         st.header("ℹ️ Information")
#         st.info(
#             "This tool scrapes comprehensive product data from Amazon and prints it to the terminal.\n\n"
#             "Data fetched includes:\n"
#             "• Product details & descriptions\n"
#             "• Pricing information\n"
#             "• Customer ratings & reviews\n"
#             "• Product specifications\n"
#             "• Images & variants\n"
#             "• Related products\n"
#             "• Q&A sections"
#         )
        
#         st.header("🎯 Usage Tips")
#         st.markdown(
#             "1. **Copy the full Amazon product URL**\n"
#             "2. **Paste it in the input field**\n"
#             "3. **Click 'Scrape Product Data'**\n"
#             "4. **Check the terminal for the scraped data**\n"
#         )
        
#         if 'last_scraped_url' in st.session_state:
#             st.header("📈 Session Info")
#             st.success(f"✅ Last scraped: {st.session_state.get('last_scraped_url', 'N/A')}")
            
#             if st.button("🗑️ Clear Session Data"):
#                 if 'last_scraped_url' in st.session_state:
#                     del st.session_state['last_scraped_url']
#                 st.rerun()

# if __name__ == "__main__":
#     main()

import streamlit as st
import os
import json
import numpy as np
import faiss
from scrape_enhanced import AmazonProductScraper
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# ----------------- CONFIG -----------------
st.set_page_config(page_title="AI Powered Web Q&A", page_icon="🤖", layout="wide")

# API keys
openai_api_key = os.getenv("OPENAI_API_KEY") or st.sidebar.text_input("Enter OpenAI API Key", type="password")
google_api_key = os.getenv("GOOGLE_API_KEY") or st.sidebar.text_input("Enter Google API Key", type="password")

if not openai_api_key or not google_api_key:
    st.warning("Please provide both OpenAI and Google API keys in the sidebar.")
    st.stop()

# ----------------- SCRAPER -----------------
def scrape_website(url):
    """Scrape Amazon product data and print to terminal."""
    try:
        chrome_driver_path = r"C:\Users\saroj mandal\OneDrive\Desktop\ai_powered_web_assistant\chromedriver.exe"
        scraper = AmazonProductScraper(chrome_driver_path)
        result = scraper.scrape_product_data(url)
        print("Scraped Data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        st.error(f"Scraping failed: {str(e)}")
        return None

# ----------------- VECTORSTORE -----------------
def split_text(scraped_text):
    """Split text into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_text(scraped_text)

def setup_vectorstore_batch(scraped_text, url, batch_size=50):
    """Embed with OpenAI in batches and create FAISS vectorstore."""
    try:
        chunks = split_text(scraped_text)
        if not chunks:
            st.error("No text chunks created from scraped data.")
            return None
        
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        texts = []
        vectors = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_vectors = embeddings.embed_documents(batch)
            vectors.extend(batch_vectors)
            texts.extend(batch)

        vectors = np.array(vectors).astype('float32')
        dimension = vectors.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)

        vectorstore = FAISS.from_embeddings(
            text_embeddings=zip(texts, vectors),
            embedding=embeddings,
            metadatas=[{"url": url}] * len(texts)
        )
        vectorstore.save_local("vectorstore")
        return vectorstore
    except Exception as e:
        st.error(f"Error setting up vector store: {str(e)}")
        return None

# ----------------- RAG CHAIN -----------------
def setup_rag(vectorstore):
    """Set up ConversationalRetrievalChain with Gemini LLM."""
    try:
        llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
        prompt_template = """
        You are an expert assistant answering questions about an Amazon product based on the provided context. Use the context to provide accurate, concise, and helpful answers. Focus on key product details like title, price, features, or reviews when relevant. If the exact answer isn't in the context, use the available information to give a reasonable response or clarify what information is missing. Avoid saying "I don't know" unless absolutely necessary. Format your answer clearly, using bullet points or short paragraphs for readability.

        Context: {context}
        Question: {question}
        Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, k=5)

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt}
        )
        return qa_chain
    except Exception as e:
        st.error(f"Error setting up RAG chain: {str(e)}")
        return None

# ----------------- STREAMLIT APP -----------------
def main():
    st.title("🤖 AI Powered Web Q&A")
    st.markdown("### Enter an Amazon product URL and ask questions about it")

    url = st.text_input("Amazon product URL:", placeholder="https://www.amazon.com/dp/PRODUCT_ID")

    if url and st.button("🔍 Scrape and Prepare Data"):
        with st.spinner("Scraping and embedding..."):
            result = scrape_website(url)
            if result and "scraped_text" in result:
                st.write(f"Scraped Text Preview: {result['scraped_text'][:200]}...")
                vectorstore = setup_vectorstore_batch(result["scraped_text"], url)
                if vectorstore:
                    st.session_state["qa_chain"] = setup_rag(vectorstore)
                    st.session_state["chat_history"] = []
                    st.session_state["last_scraped_url"] = url
                    st.session_state["vectorstore"] = vectorstore  # Store for similarity search
                    st.success("✅ Ready for Q&A!")
            else:
                st.error("❌ No valid data scraped.")

    if "qa_chain" in st.session_state:
        st.markdown("### Ask Questions About the Product")
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if question := st.chat_input("Ask a question..."):
            st.session_state["chat_history"].append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Print similarity search results to terminal
                        docs = st.session_state["vectorstore"].similarity_search(question, k=5)
                        print(f"\nSimilarity Search Results for Question: '{question}'")
                        for i, doc in enumerate(docs, 1):
                            print(f"Document {i}:")
                            print(f"Content (first 100 chars): {doc.page_content[:100]}...")
                            print(f"Metadata: {doc.metadata}")
                            print("-" * 50)

                        response = st.session_state["qa_chain"]({"question": question})
                        answer = response["answer"]
                        st.markdown(answer)
                        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Error answering question: {str(e)}")

    with st.sidebar:
        st.header("ℹ️ Info")
        if "last_scraped_url" in st.session_state:
            st.success(f"Last scraped: {st.session_state['last_scraped_url']}")
        if st.button("Reset Chat"):
            st.session_state["chat_history"] = []
            st.success("Chat history cleared.")

if __name__ == "__main__":
    main()



# AIzaSyCMwD46BollhoJJvVXAKsEOzojanzGjGi8

# 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