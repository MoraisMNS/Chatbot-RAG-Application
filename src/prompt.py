from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1) Reformulate user query using chat history
contextualize_system = (
    "Given the chat history and the latest user message, rewrite the message into a "
    "standalone question about the company or Gallery HR if needed. If it's already "
    "standalone, return it unchanged."
)
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_system),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# 2) Answering prompt (RAG)
system_prompt = (
    "You are an assistant for questions about Soft Gallery (PVT) LTD, its HR/Security "
    "policies, and the Gallery HR user manual. Answer ONLY with facts from the context.\n\n"
    "- If the answer is not in the context, say: 'I don't have that information in my materials.'\n"
    "- Be concise and helpful for a business user.\n"
    "- Do not reveal document names, versions, or authors.\n"
    "- If the user asks something off-topic (general knowledge, coding help, etc.), "
    "politely decline and say you can answer only company/HR/manual topics.\n\n"
    "{context}"
)

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])
