
# How LLMs Work

## 1. What is an LLM?

LLM stands for Large Language Model. It is an Artificial Intelligence model trained on a large amount of text data.

An LLM understands the context of text and generates human-like responses. It can answer questions, summarize information, translate languages and generate content.

Examples of LLMs are GPT, Claude and Gemini.

## 2. How Does an LLM Work?

An LLM works by processing the input text and predicting the next token.

The basic working process is:

1. The user enters a question or prompt.
2. The input text is divided into smaller units called tokens.
3. Tokens are converted into numerical representations called embeddings.
4. The Transformer model processes these representations and understands the context.
5. The model predicts the next token based on the previous tokens.
6. It continues predicting tokens until the response is completed.
7. The generated response is shown to the user.

## 3. What are Tokens?

Tokens are small pieces of text that an LLM processes.

A token can be a complete word, part of a word, or a punctuation mark.

For example:

Input: "Hello, how are you?"

The model divides this text into tokens before processing it.

Tokens help the model understand and process text efficiently.

## 4. What are Embeddings?

Embeddings are numerical representations of tokens.

Computers work with numbers, so text is converted into numerical vectors before being processed by the model.

Embeddings help the model understand relationships and similarities between words and their context.

For example, words like "king" and "queen" can have related vector representations.

## 5. How Does an LLM Generate Answers?

LLMs use a neural network architecture called the Transformer.

The Transformer uses a mechanism called Self-Attention to understand relationships between different tokens in the input.

The model predicts the next token based on the context of previous tokens.

It repeats this process until a complete response is generated.

The generated answer is then converted into readable text.

## 6. LLM Working Diagram

User Question
      |
      v
Text Tokenization
      |
      v
Token Embeddings
      |
      v
Transformer Model
      |
      v
Self-Attention
      |
      v
Next Token Prediction
      |
      v
Generated Answer

## 7. Limitations of LLMs

1. LLMs can sometimes generate incorrect information.
2. They may produce answers that sound correct but are not factual.
3. Their knowledge may not include the latest information.
4. They can misunderstand unclear questions.

Therefore, important information should always be verified using reliable sources.

## 8. How LLMs Are Used in TaxSaathi

TaxSaathi is an AI-based tax assistant project.

LLMs can help users understand tax-related questions in simple language.

In TaxSaathi, relevant tax records can be retrieved using a search system and used to provide helpful answers.

The system should avoid making unsupported claims. If the available data cannot answer a question, it should respond:

"I don't know. Please check incometax.gov.in."

## Conclusion

Large Language Models are powerful AI systems that process text and generate human-like responses.

They use tokens, embeddings, neural networks and Transformer architecture to understand context and generate answers.
