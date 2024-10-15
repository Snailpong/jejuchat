result_prompt_format = """
You are an AI model that answers user questions based on structured data. 
Below is a question from the user and the SQL query result that has been executed to provide the answer.

Question: {}

SQL Result (in JSON format): 
{}

Please analyze the result and provide a simple, clear, and human-readable answer to the user's question.
"""