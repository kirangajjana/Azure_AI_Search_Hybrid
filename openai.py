import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI  # Assuming you'll use Azure OpenAI Python library

class RAGSearchSystem:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Azure Cognitive Search Configuration
        self.search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.search_key = os.getenv('AZURE_SEARCH_KEY')
        self.search_index_name = os.getenv('AZURE_SEARCH_INDEX')

        # Azure OpenAI Configuration
        self.openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_key = os.getenv('AZURE_OPENAI_KEY')
        self.openai_deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        # Initialize clients
        self.search_credential = AzureKeyCredential(self.search_key)
        self.search_client = SearchClient(
            endpoint=self.search_endpoint, 
            index_name=self.search_index_name, 
            credential=self.search_credential
        )
        
        self.openai_client = AzureOpenAI(
            azure_endpoint=self.openai_endpoint,
            api_key=self.openai_key,
            api_version="2023-12-01-preview"  # Use the latest API version
        )

    def semantic_search(self, query, top_k=5):
        """
        Perform semantic search and retrieve most relevant documents
        
        Args:
            query (str): User's search query
            top_k (int): Number of top results to retrieve
        
        Returns:
            list: Relevant search results
        """
        try:
            search_results = self.search_client.search(
                search_text=query,
                top=top_k
            )
            return list(search_results)
        
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def generate_response(self, query, search_results):
        """
        Use OpenAI to generate a contextual response based on search results
        
        Args:
            query (str): Original user query
            search_results (list): Relevant documents from search
        
        Returns:
            str: Generated response
        """
        # Construct context from search results
        context = "\n\n".join([
            f"Title: {result.get('title', '')}\nContent: {result.get('content', '')}" 
            for result in search_results
        ])

        # Prepare prompt for OpenAI
        prompt = f"""
        Context: {context}
        
        Query: {query}
        
        Based on the provided context, generate a comprehensive and precise answer to the query.
        If the context doesn't contain sufficient information, acknowledge that transparently.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300  # Adjust as needed
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return "I'm unable to generate a response at the moment."

    def rag_search(self, query):
        """
        Complete RAG workflow: search and generate response
        
        Args:
            query (str): User's search query
        
        Returns:
            tuple: (search_results, generated_response)
        """
        # Semantic search first
        search_results = self.semantic_search(query)
        
        # Generate response using search results
        generated_response = self.generate_response(query, search_results)
        
        return search_results, generated_response

def main():
    rag_system = RAGSearchSystem()
    
    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        
        if query.lower() == 'exit':
            break
        
        search_results, response = rag_system.rag_search(query)
        
        print("\n--- Search Results ---")
        for result in search_results:
            print(f"Title: {result.get('title')}")
            print(f"Content: {result.get('content')[:200]}...\n")
        
        print("\n--- Generated Response ---")
        print(response)

if __name__ == "__main__":
    main()