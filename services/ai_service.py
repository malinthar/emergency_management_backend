from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import StructuredTool
from lib.constants import SYSTEM_PROMPT_DATA_EXTRACT
from services.tools import EmergencyTools
import os

load_dotenv()
class EmergencyResponse(BaseModel):
    response_message: str
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
            
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages(
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
        
        # Initialize tools
        self.tools = self._create_tools()
        
    def _create_tools(self):
        """Create and return the tools for the agent to use"""
        
        # 1. Data extraction tool
        extract_data_tool = StructuredTool.from_function(
            func=EmergencyTools.extract_emergency_data,
            name="extract_emergency_data",
            description="Extract structured data from an emergency transcript or message"
        )
        
        # 2. Alert emergency services tool
        alert_services_tool = StructuredTool.from_function(
            func=EmergencyTools.alert_emergency_services,
            name="alert_emergency_services",
            description="Alert relevant emergency services based on the emergency data"
        )
        
        # 3. Report generation tool
        generate_report_tool = StructuredTool.from_function(
            func=EmergencyTools.generate_report,
            name="generate_report",
            description="Generate a comprehensive report of the emergency and response"
        )
        
        # 4. Find next steps tool
        next_steps_tool = StructuredTool.from_function(
            func=EmergencyTools.find_next_steps,
            name="find_next_steps",
            description="Determine recommended next steps based on emergency data"
        )
        
        # 5. Translation tool
        translation_tool = StructuredTool.from_function(
            func=EmergencyTools.translate_to_language,
            name="translate_to_language",
            description="Translate text to the specified language"
        )
        
        return [
            extract_data_tool,
            alert_services_tool,
            generate_report_tool,
            next_steps_tool,
            translation_tool
        ]
        
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
        
        # Create agent with the LLM instance variable and tools
        agent = create_tool_calling_agent(
            llm=self.llm,
            prompt=prompt,
            tools=self.tools
        )
 
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True
        )

        try:
            raw_response = agent_executor.invoke({"query": query, "chat_history": []})
            print(raw_response)
            output = raw_response.get("output", "")
            print(f"Raw output: {output}")
            
            try:
                structured_response = self.parser.parse(output)
                # Return the model as a dictionary instead of a JSON string
                return structured_response.model_dump()
            except Exception as parsing_error:
                print(f"Error parsing output: {parsing_error}")
                # If parsing fails, return a simple response object with the raw output
                return {
                    "response_message": f"Successfully processed your request: {output}",
                    "emergency_type": None,
                    "additional_notes": f"Unable to parse structured data: {str(parsing_error)}"
                }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            error_message = f"Error processing your request: {str(e)}"
            return {
                "response_message": error_message,
                "emergency_type": None,
                "additional_notes": "An error occurred during processing"
            }




