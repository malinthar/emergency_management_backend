from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from lib.constants import SYSTEM_PROMPT_DATA_EXTRACT
import os


load_dotenv()
class EmergencyResponse(BaseModel):
    emergency_type: str  # Type of emergency (fire, flood, medical emergency, etc.)
    person_profile: dict = {  # Information about the affected person(s)
        "age": str,
        "gender": str,
        "medical_conditions": str
    }
    location: dict = {  # Location details
        "address": str,
        "landmarks": str,
        "coordinates": str
    }
    time_of_incident: str
    people_affected: int
    immediate_risks: list[str]
    resources_needed: list[str]
    additional_notes: str

class AIService:
    """
    Service to handle AI-related operations.
    This is a placeholder for the actual AI library integration.
    """
    
    def __init__(self):
        # Initialize any required resources or connections
        system_prompt = "You are a helpful AI assistant."
            
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt_template  = ChatPromptTemplate.from_messages(
         [
        ("system", 
         """{system_prompt} \n {format_instructions}"""),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
        ] 
        )
        
        # Initialize the parser
        self.parser = PydanticOutputParser(pydantic_object=EmergencyResponse)
        
    def get_response(self, query):
        """
        Process a user query and return a response.
        This would normally call an AI library.
        
        Args:
            query (str): User's query text
            
        Returns:
            str: Response to the user's query
        """
        print(f"Processing query: {query}")
        # Create prompt template with correct parser reference
        prompt = self.prompt_template.partial(
            system_prompt=SYSTEM_PROMPT_DATA_EXTRACT,
            format_instructions=self.parser.get_format_instructions()
            
        )
        
        # Define tools - currently empty but you can add tools as needed
        tools = []
        
        # Create agent with the LLM instance variable
        agent = create_tool_calling_agent(
            llm=self.llm,
            prompt=prompt,
            tools=tools
        )
 
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )

        try:
            raw_response = agent_executor.invoke({"query": query, "chat_history": []})
            print(raw_response)
            output = raw_response.get("output", [])
            print(f"Raw output: {output}")
            structured_response = self.parser.parse(output)
            #send a json response
            print(f"Structured response: {structured_response}")
            
            # Return the model as a dictionary instead of a JSON string
            # This will prevent the escape characters
            return structured_response.model_dump()
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"Error proces sing your request: {query}"




