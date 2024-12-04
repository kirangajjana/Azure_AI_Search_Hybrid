from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchFieldDataType, SearchableField
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve configuration from environment variables
Search_service_name = os.getenv('search_service_name')
Search_api_key = os.getenv('search_api_key')
endpoint = os.getenv('endpoint')

# Validate environment variables
if not all([Search_service_name, Search_api_key, endpoint]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Create AzureKeyCredential object for authentication
credential = AzureKeyCredential(Search_api_key)

# Initialize the index client with the credential
index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

class AzureCognitiveSearchManager:
    def __init__(self, endpoint, credential, index_name):
        """
        Initialize the Azure Cognitive Search Manager
        
        Args:
            endpoint (str): Azure Cognitive Search service endpoint
            credential (AzureKeyCredential): Authentication credential
            index_name (str): Name of the search index
        """
        self.endpoint = endpoint
        self.credential = credential
        self.index_name = index_name
        self.search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    def create_index(self):
        """
        Create the search index with predefined fields
        """
        # Define the fields for the index
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String, retrievable=True, searchable=True),
            SearchableField(name="content", type=SearchFieldDataType.String, retrievable=True, searchable=True),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True)
        ]
        
        # Create the index object
        index = SearchIndex(
            name=self.index_name,
            fields=fields
        )

        # Create the index using the SearchIndexClient
        try:
            index_client.create_index(index)
            print(f"Index '{self.index_name}' created successfully.")
        except Exception as e:
            print(f"Error creating index: {e}")

    def upload_documents(self, documents):
        """
        Upload documents to the search index
        
        Args:
            documents (list): List of documents to upload
        """
        if not documents:
            print("No documents to upload.")
            return

        try:
            # Split documents into batches (Azure Search allows batch size of up to 1000)
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                results = self.search_client.upload_documents(documents=batch)
                
                # Handle upload results
                for result in results:
                    print(f"Document ID: {result['key']} - Upload status: {result['status']}")
            
            print("Documents uploaded successfully.")
        
        except Exception as e:
            print(f"Error uploading documents: {e}")

    def search_by_keyword(self, search_term):
        """
        Perform a basic keyword search across all searchable fields
        
        Args:
            search_term (str): Keyword to search for
        
        Returns:
            list: Search results
        """
        try:
            results = self.search_client.search(search_term)
            search_results = list(results)
            
            print(f"\n--- Keyword Search Results for '{search_term}' ---")
            for result in search_results:
                self._print_search_result(result)
            
            return search_results
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []

    def search_by_category(self, category):
        """
        Search documents by specific category
        
        Args:
            category (str): Category to filter by
        
        Returns:
            list: Search results matching the category
        """
        try:
            results = self.search_client.search("*", filter=f"category eq '{category}'")
            search_results = list(results)
            
            print(f"\n--- Category Search Results for '{category}' ---")
            for result in search_results:
                self._print_search_result(result)
            
            return search_results
        except Exception as e:
            print(f"Error in category search: {e}")
            return []

    def advanced_search(self, search_term=None, category=None, minimum_results=1):
        """
        Perform an advanced search with multiple optional parameters
        
        Args:
            search_term (str, optional): Keyword to search for
            category (str, optional): Category to filter by
            minimum_results (int, optional): Minimum number of results to return
        
        Returns:
            list: Advanced search results
        """
        try:
            # Construct filter condition
            filter_condition = None
            if category:
                filter_condition = f"category eq '{category}'"
            
            # Perform search
            results = self.search_client.search(
                search_text=search_term or "*",
                filter=filter_condition,
                top=minimum_results  # Limit results
            )
            
            search_results = list(results)
            
            print(f"\n--- Advanced Search Results ---")
            for result in search_results:
                self._print_search_result(result)
            
            return search_results
        except Exception as e:
            print(f"Error in advanced search: {e}")
            return []

    def _print_search_result(self, result):
        """
        Helper method to print search result details
        
        Args:
            result (dict): Search result to print
        """
        print(f"Title: {result.get('title')}")
        print(f"Category: {result.get('category')}")
        print(f"Content: {result.get('content')[:200]}...")  # Truncate long content
        print("---")

def main():
    """
    Main function to demonstrate Azure Cognitive Search functionality
    """
    # Define your index name
    index_name = "kirangajjana"

    # Sample documents (kept the same as previous implementation)
    sample_documents = [
        {"id": "1", "title": "Azure AI Search", "content": "Azure AI Search is a powerful tool for enterprise search.", "category": "Azure"},
  {"id": "2", "title": "RAG Systems", "content": "RAG combines retrieval and generation for better answers.", "category": "AI"},
  {"id": "3", "title": "Machine Learning", "content": "ML enables systems to learn and adapt over time.", "category": "ML"},
  {"id": "4", "title": "Natural Language Processing", "content": "NLP techniques enable machines to understand human language.", "category": "AI"},
  {"id": "5", "title": "Computer Vision", "content": "Computer vision is transforming image recognition and analysis.", "category": "Vision"},
  {"id": "6", "title": "Azure Functions", "content": "Azure Functions offer a serverless compute service.", "category": "Azure"},
  {"id": "7", "title": "Generative AI", "content": "Generative AI creates new content using machine learning.", "category": "AI"},
  {"id": "8", "title": "Data Science", "content": "Data science combines statistics and AI to extract insights.", "category": "Data"},
  {"id": "9", "title": "Cloud Computing", "content": "Cloud computing enables scalable and on-demand IT resources.", "category": "Cloud"},
  {"id": "10", "title": "IoT Edge", "content": "IoT Edge provides analytics and insights at the device level.", "category": "IoT"},
  {"id": "11", "title": "Deep Learning", "content": "Deep learning models are used for complex pattern recognition.", "category": "AI"},
  {"id": "12", "title": "Quantum Computing", "content": "Quantum computing harnesses quantum mechanics for faster computations.", "category": "Tech"},
  {"id": "13", "title": "Blockchain Technology", "content": "Blockchain provides secure, decentralized transaction management.", "category": "Tech"},
  {"id": "14", "title": "5G Technology", "content": "5G offers high-speed connectivity for advanced mobile networks.", "category": "Tech"},
  {"id": "15", "title": "Edge Computing", "content": "Edge computing processes data closer to the source for faster insights.", "category": "Cloud"},
    ]
    
    # Create search manager
    search_manager = AzureCognitiveSearchManager(endpoint, credential, index_name)
    
    # Create index and upload documents
    search_manager.create_index()
    search_manager.upload_documents(sample_documents)

    # Search menu
    while True:
        print("\n--- Azure Cognitive Search Menu ---")
        print("1. Keyword Search")
        print("2. Category Search")
        print("3. Advanced Search")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            # Keyword Search
            search_term = input("Enter keyword to search: ")
            search_manager.search_by_keyword(search_term)
        
        elif choice == '2':
            # Category Search
            category = input("Enter category to search (AI, Azure, Cloud, etc.): ")
            search_manager.search_by_category(category)
        
        elif choice == '3':
            # Advanced Search
            print("\nAdvanced Search Options:")
            search_term = input("Enter keyword (optional, press enter to skip): ")
            category = input("Enter category (optional, press enter to skip): ")
            min_results = input("Minimum number of results (default is 1): ")
            
            # Convert minimum results to integer, default to 1 if not provided
            min_results = int(min_results) if min_results.isdigit() else 1
            
            search_manager.advanced_search(search_term, category, min_results)
        
        elif choice == '4':
            print("Exiting Azure Cognitive Search...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()