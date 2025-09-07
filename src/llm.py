from src.config import OPENAI_API_KEY
from src.pinecone_vectorstore import get_vectorstore
from src.prompt import contextualize_prompt, answer_prompt
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0)

vectorstore = get_vectorstore()

base_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 8, "fetch_k": 24, "lambda_mult": 0.6}
)

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

history_aware_retriever = create_history_aware_retriever(
    llm, compression_retriever, contextualize_prompt
)

qa_chain = create_stuff_documents_chain(llm, answer_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
