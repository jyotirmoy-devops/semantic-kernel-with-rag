import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion,  OpenAIChatPromptExecutionSettings
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents import ChatHistoryAgentThread
from semantic_kernel.contents import ChatHistorySummarizationReducer
from tools.docintelligence_app import DocIntelligenceApp
from semantic_kernel.filters import FilterTypes, FunctionInvocationContext
from semantic_kernel.kernel import Kernel
from typing import Awaitable, Callable
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents.strategies import DefaultTerminationStrategy, SequentialSelectionStrategy
kernel = Kernel()


async def function_invocation_filter(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    # this runs before the function is called
    print(f"  ---> Calling Plugin {context.function.plugin_name}.{context.function.name} with arguments `{context.arguments}`")
    # let's await the function call
    await next(context)
    # this runs after our functions has been called
    print(f"  ---> Plugin response from [{context.function.plugin_name}.{context.function.name} is `{context.result}`")
#kernel.add_filter(FilterTypes.FUNCTION_INVOCATION, function_invocation_filter)
chat_history_with_reducer = ChatHistorySummarizationReducer(
    service=AzureChatCompletion(),
    target_count=2,
    threshold_count=2,
    auto_reduce=True,
)
chat_history_with_reducer.clear()
document_pull_agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="document_pull_agent",
    instructions="You are an AI assistant that helps pulls the content of a document that the user provides.",
    plugins=[DocIntelligenceApp()]
)

document_summarizer_agent = ChatCompletionAgent(
    service=AzureChatCompletion(),
    name="document_summarizer_agent",
    instructions="You are an AI assistant that helps answers questions about the document that the user provides."
)
group_chat = AgentGroupChat(
    agents=[document_pull_agent, document_summarizer_agent],
    selection_strategy=SequentialSelectionStrategy(), # Use sequential selection (round-robin)
    termination_strategy=DefaultTerminationStrategy(maximum_iterations=4), # 2 iterations for each agent
)
# settings = OpenAIChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())
# settings.response_format = DocumentAnalysisResult
# async def main():
#     user_messages = [
#     "Analyze the document doc.pdf and then summarize it for me.",
#     ]
#     thread = ChatHistoryAgentThread(chat_history=chat_history_with_reducer)
#     for user_message in user_messages:
#         print("*** User:", user_message)
        
#         # get our response from the agent
#         response = await simple_agent.get_response(messages=user_message, thread=thread, settings=settings)
#         print("*** Agent:", response.content)
    
#     # save the thread with all the existing messages and responses
#     thread = response.thread

    # # print the final conversation, so we can see what happens in thread
    # print("-" * 25)
    # async for m in thread.get_messages():
    #     print(m.role, m.content)
async def run_group_chat(group_chat: AgentGroupChat, question: str):
    
    await group_chat.add_chat_message(question)
    
    async for response in group_chat.invoke():
        print(f"*** {response.role} - {response.name or '*'}: '{response.content}'")
    print(f"*** History length: {len(group_chat.history)}")
    
    # We can manually reset the state to keep the chat going
    # simple_group_chat.is_complete = False
    return group_chat.history

# Test the simple group chat with a question
async def main():

    # Test the simple group chat with a question
    question = "Analyze the document docb.pdf and then tell me equiments being used for Temperature testing."
    full_history = await run_group_chat(group_chat, question)
if __name__ == "__main__":
    asyncio.run(main())