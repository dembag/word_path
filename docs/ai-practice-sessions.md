# AI practice sessions 
 
Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to your OpenAI API key. 
Set `OPENAI_MODEL` to the model used for question and narrative generation. 
Do not commit `.env` or share its contents. 

AI credentials are needed when generating a session or its narrative. The app 
can start without an API key, but an AI generation request will return a 
recoverable error if configuration is missing or the provider is unavailable. 
Failed question generation does not fall back to the fixed test scenarios. 

`OPENAI_EMBEDDING_MODEL` is not needed for practice question generation.

# Session measures

Answers with a negative elapsed time are excluded. All other submitted answers
count toward `answered_count`; there is no 30-second cutoff. The response-time
categories are:

- Under 10 seconds: independent.
- 10 seconds to under 20 seconds: verbal prompt.
- 20 seconds or more: modeled.

Questions with no submitted answer when the session is completed are unanswered
and are excluded from `answered_count`.

Accuracy is `correct_count / answered_count * 100`. Each support rate is its
category count divided by `answered_count`, multiplied by 100. These rates are
`None` when `answered_count` is zero.

Use this sample to check the saved summary: 4 submitted answers, 3 correct, 2
independent, 1 verbal, and 1 modeled should produce accuracy 75%, independent
50%, verbal 25%, and modeled 25%.