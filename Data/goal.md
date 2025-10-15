The goal of this challenge is to design and implement a ChatBot API that acts as a Sales AI Agent for an online bike shop.

The Sales Agent should be able to:

Conduct customer consultations via an API (REST or WebSocket).
Recommend products from a given product catalog.
Detect customer interest and guide the conversation.
Collect customer details (name, email, phone number) when interest is confirmed.
Create a Lead in the internal CRM system.
Schedule an Appointment with a real sales consultant.
This challenge focuses on automation, data-driven logic, and AI techniques to simulate a realistic sales workflow.

2. Focus of the Assignment
The implementation should emphasize:

Automation – Handle the sales flow with minimal manual intervention.
Data – Use the provided product catalog as the only source for recommendations.
AI Best Practices – Apply techniques like Prompt Engineering, Retrieval-Augmented Generation (RAG), and Vector Search.
Scalability – Package the solution for deployment (e.g., Docker).
Flexibility – Allow the option of using local LLMs in addition to APIs like OpenAI.
3. Tasks
Overview
Conversation API
As a customer, I want to interact with the Sales Agent through an API so that I can receive fluent and natural responses to my questions.

Product Recommendation
As a customer, I want the agent to recommend bikes from the catalog based on my preferences (type, price, usage) so that I can find a suitable product.

Lead Creation
As a sales organization, I want the agent to collect customer details (name, email, phone number) once interest is confirmed, so that a lead can be created in our CRM system.

Appointment Scheduling (OUT_OF_SCOPE) As a customer, I want the agent to book an appointment with a real sales consultant so that I can discuss my needs in more detail.

FAQ
As a customer, I want the agent to also answer general questions (e.g., delivery, warranty, services) from an FAQ knowledge base, so that I get a complete consultation experience.

3.1 Conversation API
Expose the Sales Agent as an API (REST or WebSocket).
Accept customer messages and return agent responses.
Maintain a simple multi-turn conversation (context awareness).
3.2 Product Recommendations
Use the provided product catalog bikes
Provide recommendations based on the customer's message.
3.3 Lead Generation
When customer interest is confirmed, the agent must collect:

Customer name
Email address
Phone number
Using this information, the agent creates a Lead in the CRM system via a API POST /ctream-crm/api/v1/leads

Request Payload

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+491234567"
}
3.4 Appointment Scheduling (OUT_OF_SCOPE)
After lead creation, and the user confirms for an appointment, the agent should create an appointment.
Appointment must be created via following API POST
Request

{
  "conversation_id": "XXX",
  "customer_id": "XXX"
}
3.5 FAQ
In addition to the product catalog, the agent must also use unstructured text data from: faq.txt
4. Requirements & Evaluation
Language: Python
API: REST or WebSocket
Data: Use only /data/bike_shop.json
AI:
Visible prompt engineering
Apply RAG for product recommendations
Use vector search (e.g., FAISS, Qdrant, Pinecone)
OpenAI, HuggingFace or local LLMs allowed
Evaluation Criteria:

Clean API design and error handling
Correct use of RAG and vector DB
Demonstrated prompt engineering
Deployable with Docker
Flexible (API or local LLM)
Natural and fluent conversation flow
Code quality and maintainability
