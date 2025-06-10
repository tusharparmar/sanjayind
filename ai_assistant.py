import google.generativeai as genai
import logging
from config import Config
from knowledge_base import KnowledgeBase

class AIAssistant:
    """AI Assistant using Google's Gemini API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_base = KnowledgeBase()
        
        # Configure Gemini API
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.logger.info("Gemini AI Assistant initialized successfully")
        else:
            self.model = None
            self.logger.error("Gemini API key not provided")
    
    def process_query(self, query, context=None):
        """
        Process user query with context and return AI response
        
        Args:
            query (str): User's text query
            context (dict): Additional context including screen content, user info, etc.
        
        Returns:
            str: AI response
        """
        if not self.model:
            return "AI Assistant is not available. Please check your Gemini API key configuration."
        
        try:
            # Build enhanced prompt with context
            enhanced_prompt = self._build_enhanced_prompt(query, context)
            
            # Generate response using Gemini
            response = self.model.generate_content(enhanced_prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _build_enhanced_prompt(self, query, context):
        """
        Build an enhanced prompt with context and knowledge base information
        
        Args:
            query (str): User's original query
            context (dict): Additional context
        
        Returns:
            str: Enhanced prompt for Gemini
        """
        prompt_parts = []
        
        # System prompt for AI assistant personality
        system_prompt = """You are a helpful AI voice assistant with a friendly, professional female persona. 
        You are integrated into a web application to help users with their tasks and questions. 
        You should provide clear, concise, and actionable responses. 
        When possible, guide users through step-by-step processes.
        Keep your responses conversational and natural for voice interaction."""
        
        prompt_parts.append(system_prompt)
        
        # Add knowledge base context if relevant
        if self.knowledge_base:
            relevant_knowledge = self.knowledge_base.search_relevant(query)
            if relevant_knowledge:
                prompt_parts.append(f"\nRelevant knowledge base information:\n{relevant_knowledge}")
        
        # Add screen context if available
        if context and context.get('screenContent'):
            screen_content = context['screenContent']
            prompt_parts.append(f"\nCurrent screen content context:\n{screen_content}")
        
        # Add user context if available
        if context and context.get('userInfo'):
            user_info = context['userInfo']
            prompt_parts.append(f"\nUser context: {user_info}")
        
        # Add the actual user query
        prompt_parts.append(f"\nUser question: {query}")
        
        # Add response guidelines
        response_guidelines = """
        Please provide a helpful response that:
        1. Directly addresses the user's question
        2. Uses information from the screen context if relevant
        3. References knowledge base information when applicable
        4. Is suitable for voice delivery (conversational tone)
        5. Includes step-by-step guidance when appropriate
        6. Is concise but complete
        """
        
        prompt_parts.append(response_guidelines)
        
        return "\n".join(prompt_parts)
    
    def analyze_screen_content(self, screen_data, user_query=None):
        """
        Analyze screen content and provide contextual assistance
        
        Args:
            screen_data (dict): Screen capture data including text, elements, etc.
            user_query (str): Optional specific user query about the screen
        
        Returns:
            str: Analysis and suggestions
        """
        if not self.model:
            return "Screen analysis is not available."
        
        try:
            analysis_prompt = f"""
            Analyze the following screen content and provide helpful insights:
            
            Screen Content: {screen_data}
            
            {f"User Question: {user_query}" if user_query else ""}
            
            Please provide:
            1. A summary of what's visible on the screen
            2. Potential actions the user might want to take
            3. Any issues or opportunities you notice
            4. Step-by-step guidance if applicable
            
            Keep the response conversational and actionable.
            """
            
            response = self.model.generate_content(analysis_prompt)
            return response.text.strip() if response and response.text else "Unable to analyze screen content."
            
        except Exception as e:
            self.logger.error(f"Error analyzing screen content: {e}")
            return f"Error analyzing screen: {str(e)}"
    
    def get_workflow_guidance(self, workflow_name, current_step=None):
        """
        Get guidance for a specific workflow
        
        Args:
            workflow_name (str): Name of the workflow
            current_step (int): Current step in the workflow
        
        Returns:
            str: Workflow guidance
        """
        if not self.knowledge_base:
            return "Workflow guidance is not available."
        
        workflow = self.knowledge_base.get_workflow(workflow_name)
        if not workflow:
            return f"Workflow '{workflow_name}' not found."
        
        try:
            guidance_prompt = f"""
            Provide guidance for the following workflow:
            
            Workflow: {workflow}
            Current Step: {current_step if current_step else 'Starting'}
            
            Please provide:
            1. Clear instructions for the current or next step
            2. What the user should expect to see
            3. Common issues and how to resolve them
            4. Next steps in the process
            
            Make the guidance conversational and easy to follow.
            """
            
            response = self.model.generate_content(guidance_prompt)
            return response.text.strip() if response and response.text else "Unable to provide workflow guidance."
            
        except Exception as e:
            self.logger.error(f"Error getting workflow guidance: {e}")
            return f"Error getting guidance: {str(e)}"

