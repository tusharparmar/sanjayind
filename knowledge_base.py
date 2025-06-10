import json
import os
import logging
from typing import List, Dict, Any, Optional
from config import Config

class KnowledgeBase:
    """Knowledge base system for workflows and operational guidance"""
    
    def __init__(self, knowledge_file=None):
        self.logger = logging.getLogger(__name__)
        self.knowledge_file = knowledge_file or Config.KNOWLEDGE_BASE_PATH
        self.knowledge_data = {}
        self.workflows = {}
        self.faqs = {}
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_data = json.load(f)
                
                # Extract different sections
                self.workflows = self.knowledge_data.get('workflows', {})
                self.faqs = self.knowledge_data.get('faqs', [])
                
                self.logger.info(f"Knowledge base loaded: {len(self.workflows)} workflows, {len(self.faqs)} FAQs")
            else:
                self.logger.warning(f"Knowledge base file not found: {self.knowledge_file}")
                self._create_default_knowledge_base()
                
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {e}")
            self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self):
        """Create a default knowledge base if none exists"""
        default_knowledge = {
            "workflows": {
                "login_process": {
                    "title": "User Login Process",
                    "description": "Step-by-step guide for user authentication",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Navigate to Login Page",
                            "description": "Click on the 'Login' or 'Sign In' button",
                            "expected_elements": ["login button", "sign in link"],
                            "common_issues": ["Button not visible", "Page not loading"]
                        },
                        {
                            "step": 2,
                            "title": "Enter Credentials",
                            "description": "Fill in your username/email and password",
                            "expected_elements": ["username field", "password field"],
                            "common_issues": ["Forgot password", "Invalid credentials"]
                        },
                        {
                            "step": 3,
                            "title": "Submit Form",
                            "description": "Click the login button to authenticate",
                            "expected_elements": ["submit button", "login button"],
                            "common_issues": ["Form validation errors", "Server errors"]
                        }
                    ],
                    "troubleshooting": {
                        "forgot_password": "Click 'Forgot Password' link and follow email instructions",
                        "account_locked": "Contact support or wait for automatic unlock",
                        "invalid_credentials": "Double-check username and password spelling"
                    }
                },
                "form_submission": {
                    "title": "Form Submission Process",
                    "description": "General guidance for filling and submitting forms",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Review Required Fields",
                            "description": "Identify all required fields marked with asterisks (*)",
                            "expected_elements": ["required field indicators", "form labels"],
                            "common_issues": ["Missing required fields", "Unclear labels"]
                        },
                        {
                            "step": 2,
                            "title": "Fill Form Data",
                            "description": "Enter accurate information in all fields",
                            "expected_elements": ["input fields", "dropdown menus", "checkboxes"],
                            "common_issues": ["Validation errors", "Format requirements"]
                        },
                        {
                            "step": 3,
                            "title": "Validate and Submit",
                            "description": "Review information and submit the form",
                            "expected_elements": ["submit button", "review section"],
                            "common_issues": ["Validation failures", "Network errors"]
                        }
                    ],
                    "troubleshooting": {
                        "validation_error": "Check field formats and required information",
                        "submission_failed": "Check internet connection and try again",
                        "data_lost": "Use browser back button or refresh to recover"
                    }
                },
                "navigation": {
                    "title": "Website Navigation",
                    "description": "How to navigate through website sections",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Use Main Menu",
                            "description": "Look for navigation menu at top or side of page",
                            "expected_elements": ["navigation menu", "menu items"],
                            "common_issues": ["Menu not visible", "Mobile menu hidden"]
                        },
                        {
                            "step": 2,
                            "title": "Use Breadcrumbs",
                            "description": "Follow breadcrumb trail to understand location",
                            "expected_elements": ["breadcrumb navigation"],
                            "common_issues": ["Breadcrumbs missing", "Unclear hierarchy"]
                        },
                        {
                            "step": 3,
                            "title": "Use Search Function",
                            "description": "Use site search to find specific content",
                            "expected_elements": ["search box", "search button"],
                            "common_issues": ["No search results", "Search not working"]
                        }
                    ],
                    "troubleshooting": {
                        "lost_navigation": "Use browser back button or site logo to return home",
                        "broken_links": "Try alternative navigation paths or contact support",
                        "mobile_issues": "Look for hamburger menu icon on mobile devices"
                    }
                }
            },
            "faqs": [
                {
                    "question": "How do I reset my password?",
                    "answer": "Click on 'Forgot Password' on the login page, enter your email address, and follow the instructions sent to your email.",
                    "category": "authentication",
                    "keywords": ["password", "reset", "forgot", "login"]
                },
                {
                    "question": "Why is the page not loading?",
                    "answer": "This could be due to internet connectivity issues, server problems, or browser cache. Try refreshing the page, clearing your browser cache, or checking your internet connection.",
                    "category": "technical",
                    "keywords": ["loading", "page", "error", "connection"]
                },
                {
                    "question": "How do I contact support?",
                    "answer": "You can contact support through the 'Contact Us' page, email support@company.com, or use the live chat feature if available.",
                    "category": "support",
                    "keywords": ["support", "contact", "help", "assistance"]
                },
                {
                    "question": "How do I save my progress?",
                    "answer": "Most forms auto-save your progress. Look for 'Save Draft' buttons or ensure you're logged in for automatic saving.",
                    "category": "functionality",
                    "keywords": ["save", "progress", "draft", "auto-save"]
                }
            ],
            "common_elements": {
                "buttons": ["submit", "save", "cancel", "next", "previous", "login", "logout"],
                "form_fields": ["email", "password", "name", "phone", "address", "date"],
                "navigation": ["menu", "breadcrumbs", "search", "home", "back"],
                "indicators": ["required field", "error message", "success message", "loading"]
            },
            "troubleshooting_guide": {
                "browser_issues": {
                    "clear_cache": "Clear browser cache and cookies",
                    "disable_extensions": "Disable browser extensions temporarily",
                    "try_incognito": "Try using incognito/private browsing mode"
                },
                "form_issues": {
                    "validation_errors": "Check all required fields are filled correctly",
                    "format_errors": "Ensure data matches required format (email, phone, etc.)",
                    "submission_errors": "Check internet connection and try again"
                },
                "navigation_issues": {
                    "broken_links": "Use alternative navigation or contact support",
                    "missing_pages": "Check URL spelling or use site search",
                    "access_denied": "Ensure you're logged in with proper permissions"
                }
            }
        }
        
        # Save default knowledge base
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(default_knowledge, f, indent=2, ensure_ascii=False)
            
            self.knowledge_data = default_knowledge
            self.workflows = default_knowledge['workflows']
            self.faqs = default_knowledge['faqs']
            
            self.logger.info("Default knowledge base created")
        except Exception as e:
            self.logger.error(f"Error creating default knowledge base: {e}")
    
    def search_relevant(self, query: str, max_results: int = 5) -> str:
        """
        Search for relevant knowledge based on query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
        
        Returns:
            str: Formatted relevant knowledge
        """
        query_lower = query.lower()
        relevant_items = []
        
        # Search FAQs
        for faq in self.faqs:
            if any(keyword in query_lower for keyword in faq.get('keywords', [])):
                relevant_items.append({
                    'type': 'FAQ',
                    'title': faq['question'],
                    'content': faq['answer'],
                    'relevance': self._calculate_relevance(query_lower, faq.get('keywords', []))
                })
        
        # Search workflows
        for workflow_id, workflow in self.workflows.items():
            workflow_keywords = [workflow_id] + workflow.get('title', '').lower().split()
            if any(keyword in query_lower for keyword in workflow_keywords):
                relevant_items.append({
                    'type': 'Workflow',
                    'title': workflow['title'],
                    'content': workflow['description'],
                    'workflow_id': workflow_id,
                    'relevance': self._calculate_relevance(query_lower, workflow_keywords)
                })
        
        # Sort by relevance and limit results
        relevant_items.sort(key=lambda x: x['relevance'], reverse=True)
        relevant_items = relevant_items[:max_results]
        
        # Format results
        if not relevant_items:
            return "No specific guidance found for this query."
        
        formatted_results = []
        for item in relevant_items:
            if item['type'] == 'FAQ':
                formatted_results.append(f"Q: {item['title']}\nA: {item['content']}")
            elif item['type'] == 'Workflow':
                formatted_results.append(f"Workflow: {item['title']}\n{item['content']}")
        
        return "\n\n".join(formatted_results)
    
    def _calculate_relevance(self, query: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matches"""
        if not keywords:
            return 0.0
        
        matches = sum(1 for keyword in keywords if keyword.lower() in query)
        return matches / len(keywords)
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get specific workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def get_workflow_step(self, workflow_id: str, step_number: int) -> Optional[Dict[str, Any]]:
        """Get specific step from a workflow"""
        workflow = self.get_workflow(workflow_id)
        if workflow and 'steps' in workflow:
            for step in workflow['steps']:
                if step.get('step') == step_number:
                    return step
        return None
    
    def get_troubleshooting(self, workflow_id: str, issue: str) -> Optional[str]:
        """Get troubleshooting information for a specific issue"""
        workflow = self.get_workflow(workflow_id)
        if workflow and 'troubleshooting' in workflow:
            return workflow['troubleshooting'].get(issue)
        return None
    
    def get_all_entries(self) -> Dict[str, Any]:
        """Get all knowledge base entries"""
        return self.knowledge_data
    
    def add_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]):
        """Add a new workflow to the knowledge base"""
        self.workflows[workflow_id] = workflow_data
        self.knowledge_data['workflows'] = self.workflows
        self._save_knowledge_base()
    
    def add_faq(self, faq_data: Dict[str, Any]):
        """Add a new FAQ to the knowledge base"""
        self.faqs.append(faq_data)
        self.knowledge_data['faqs'] = self.faqs
        self._save_knowledge_base()
    
    def _save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_data, f, indent=2, ensure_ascii=False)
            self.logger.info("Knowledge base saved")
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {e}")
    
    def search_workflows_by_context(self, context: Dict[str, Any]) -> List[str]:
        """
        Search for relevant workflows based on screen context
        
        Args:
            context (dict): Screen context including elements, text, etc.
        
        Returns:
            List[str]: List of relevant workflow IDs
        """
        relevant_workflows = []
        
        if not context:
            return relevant_workflows
        
        screen_text = context.get('text', '').lower()
        elements = context.get('elements', [])
        
        # Check each workflow for relevance
        for workflow_id, workflow in self.workflows.items():
            relevance_score = 0
            
            # Check if workflow steps match screen elements
            for step in workflow.get('steps', []):
                expected_elements = step.get('expected_elements', [])
                for expected in expected_elements:
                    if expected.lower() in screen_text or any(expected.lower() in str(elem).lower() for elem in elements):
                        relevance_score += 1
            
            # Check workflow title and description
            title_words = workflow.get('title', '').lower().split()
            desc_words = workflow.get('description', '').lower().split()
            
            for word in title_words + desc_words:
                if word in screen_text:
                    relevance_score += 0.5
            
            if relevance_score > 0:
                relevant_workflows.append((workflow_id, relevance_score))
        
        # Sort by relevance and return workflow IDs
        relevant_workflows.sort(key=lambda x: x[1], reverse=True)
        return [workflow_id for workflow_id, _ in relevant_workflows[:3]]

