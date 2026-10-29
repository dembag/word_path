# AI practice sessions 
 
Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to your OpenAI API key. 
Set `OPENAI_MODEL` to the model used for question and narrative generation. 
Do not commit `.env` or share its contents. 

AI credentials are needed when generating a session or its narrative. The app 
can start without an API key, but an AI generation request will return a 
recoverable error if configuration is missing or the provider is unavailable. 
Failed question generation does not fall back to the fixed test scenarios. 

`OPENAI_EMBEDDING_MODEL` is not needed for practice question generation.