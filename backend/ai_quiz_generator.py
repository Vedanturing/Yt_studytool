"""
AI-Powered Quiz Generator
Uses OpenAI and Google Gemini APIs to generate real quiz questions based on topics and concepts
"""

import os
import logging
import json
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import AI configuration
try:
    from ai_config import AIConfig
except ImportError:
    # Fallback if config not available
    class AIConfig:
        @classmethod
        def get_gemini_model(cls):
            return 'gemini-1.5-pro'
        @classmethod
        def is_paid_user(cls):
            return True
        @classmethod
        def get_quota_info(cls):
            return "Pro Tier: Unlimited requests"

# Try to import AI libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

class AIQuizGenerator:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        
        # Initialize OpenAI
        # if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        #     try:
        #         openai.api_key = os.getenv('OPENAI_API_KEY')
        #         self.openai_client = openai
        #         logger.info("✅ OpenAI client initialized")
        #     except Exception as e:
        #         logger.error(f"❌ Failed to initialize OpenAI: {e}")
        
        # Initialize Gemini
        if GEMINI_AVAILABLE and AIConfig.GEMINI_API_KEY:
            try:
                genai.configure(api_key=AIConfig.GEMINI_API_KEY)
                model_name = AIConfig.get_gemini_model()
                self.gemini_model = genai.GenerativeModel(model_name)
                quota_info = AIConfig.get_quota_info()
                logger.info(f"✅ Gemini model initialized with {model_name} ({quota_info})")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
    
    def generate_quiz_questions(self, subject: str, unit: str, topics: List[str], 
                              num_questions: int = 10, difficulty: str = "medium") -> List[Dict]:
        """
        Generate quiz questions using AI APIs with Gemini as primary source
        """
        try:
            logger.info(f"Generating {num_questions} questions for {subject} - {unit}")
            
            # Create context from topics
            context = self._create_context(subject, unit, topics)
            
            # Try Gemini first (primary source), then OpenAI, then fallback
            questions = []
            
            if self.gemini_model:
                questions = self._generate_with_gemini(context, num_questions, difficulty)
            
            if not questions and self.openai_client:
                questions = self._generate_with_openai(context, num_questions, difficulty)
            
            # If no AI questions, use realistic fallback questions
            if not questions:
                logger.warning("⚠️ AI APIs not available or failed, using realistic fallback questions")
                questions = self._generate_fallback_questions(subject, unit, topics, num_questions, difficulty)
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating quiz questions: {e}")
            logger.info("🔄 Using realistic fallback questions due to error")
            return self._generate_fallback_questions(subject, unit, topics, num_questions, difficulty)
    
    def _create_context(self, subject: str, unit: str, topics: List[str]) -> str:
        """Create context string for AI generation"""
        topics_text = ", ".join(topics)
        return f"""
        Subject: {subject}
        Unit: {unit}
        Topics: {topics_text}
        
        Generate quiz questions that test understanding of these specific topics and concepts.
        Questions should be relevant to the subject matter and appropriate for the difficulty level.
        """
    
    def _generate_with_openai(self, context: str, num_questions: int, difficulty: str) -> List[Dict]:
        """Generate questions using OpenAI API"""
        try:
            prompt = f"""
            {context}
            
            Generate {num_questions} multiple choice questions with the following requirements:
            - Difficulty level: {difficulty}
            - Each question should have 4 options (A, B, C, D)
            - Include one correct answer
            - Provide a brief explanation for the correct answer
            - Questions should test understanding, not just memorization
            
            Format the response as a JSON array with the following structure:
            [
                {{
                    "id": 1,
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "concept": "Concept being tested",
                    "question_type": "mcq",
                    "difficulty": "{difficulty}",
                    "explanation": "Explanation of why this is correct"
                }}
            ]
            
            Return only the JSON array, no additional text.
            """
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating quiz questions for students."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            if content.startswith('[') and content.endswith(']'):
                questions = json.loads(content)
                logger.info(f"✅ Generated {len(questions)} questions with OpenAI")
                return questions
            else:
                # Try to find JSON in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx + 1]
                    questions = json.loads(json_str)
                    logger.info(f"✅ Generated {len(questions)} questions with OpenAI")
                    return questions
                    
        except Exception as e:
            logger.error(f"Error with OpenAI generation: {e}")
        
        return []
    
    def _generate_with_gemini(self, context: str, num_questions: int, difficulty: str) -> List[Dict]:
        """Generate questions using Google Gemini API"""
        try:
            prompt = f"""
            {context}
            
            Generate {num_questions} high-quality multiple choice questions with the following requirements:
            - Difficulty level: {difficulty}
            - Each question should have 4 realistic options (A, B, C, D)
            - Include exactly one correct answer
            - Provide a clear, educational explanation for the correct answer
            - Questions should test deep understanding, not just memorization
            - Make questions relevant to the specific topics provided
            - Avoid placeholder text like "{{topic}}" - use actual topic names
            - Ensure all options are plausible but only one is correct
            
            Format the response as a JSON array with the following structure:
            [
                {{
                    "id": 1,
                    "question": "Specific question about the topic?",
                    "options": ["Realistic option A", "Realistic option B", "Realistic option C", "Realistic option D"],
                    "correct_answer": "Realistic option A",
                    "concept": "Specific concept being tested",
                    "question_type": "mcq",
                    "difficulty": "{difficulty}",
                    "explanation": "Clear explanation of why this answer is correct"
                }}
            ]
            
            Make sure to:
            1. Use actual topic names from the context
            2. Create realistic, educational questions
            3. Provide meaningful explanations
            4. Test understanding of concepts, not just facts
            
            Return only the JSON array, no additional text.
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text.strip()
            
            # Try to extract JSON from response
            if content.startswith('[') and content.endswith(']'):
                questions = json.loads(content)
                logger.info(f"✅ Generated {len(questions)} questions with Gemini")
                return questions
            else:
                # Try to find JSON in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx + 1]
                    questions = json.loads(json_str)
                    logger.info(f"✅ Generated {len(questions)} questions with Gemini")
                    return questions
                    
        except Exception as e:
            logger.error(f"Error with Gemini generation: {e}")
        
        return []
    
    def _generate_fallback_questions(self, subject: str, unit: str, topics: List[str], 
                                   num_questions: int, difficulty: str) -> List[Dict]:
        """Generate realistic fallback questions when AI APIs are not available"""
        logger.info("Using realistic fallback question generation")
        
        questions = []
        
        # Subject-specific question templates
        if "operating system" in subject.lower():
            questions = self._generate_os_fallback_questions(unit, topics, num_questions, difficulty)
        elif "software engineering" in subject.lower():
            questions = self._generate_se_fallback_questions(unit, topics, num_questions, difficulty)
        elif "data analytics" in subject.lower():
            questions = self._generate_da_fallback_questions(unit, topics, num_questions, difficulty)
        else:
            questions = self._generate_generic_fallback_questions(subject, unit, topics, num_questions, difficulty)
        
        logger.info(f"✅ Generated {len(questions)} realistic fallback questions")
        return questions
    
    def _generate_os_fallback_questions(self, unit: str, topics: List[str], num_questions: int, difficulty: str) -> List[Dict]:
        """Generate Operating System specific fallback questions"""
        questions = []
        
        # OS-specific question bank
        os_questions = [
            {
                "question": "What is the primary function of an operating system?",
                "options": [
                    "To manage hardware and software resources",
                    "To only run applications",
                    "To connect to the internet",
                    "To store user data"
                ],
                "correct_answer": "To manage hardware and software resources",
                "explanation": "The primary function of an OS is to manage hardware and software resources efficiently."
            },
            {
                "question": "Which scheduling algorithm provides the shortest average waiting time?",
                "options": [
                    "Shortest Job First (SJF)",
                    "First Come First Serve (FCFS)",
                    "Round Robin",
                    "Priority Scheduling"
                ],
                "correct_answer": "Shortest Job First (SJF)",
                "explanation": "SJF provides the shortest average waiting time by executing the shortest job first."
            },
            {
                "question": "What is virtual memory used for?",
                "options": [
                    "To extend RAM using disk space",
                    "To increase CPU speed",
                    "To improve network performance",
                    "To enhance graphics quality"
                ],
                "correct_answer": "To extend RAM using disk space",
                "explanation": "Virtual memory extends RAM by using disk space as additional memory."
            },
            {
                "question": "Which memory management technique prevents memory fragmentation?",
                "options": [
                    "Paging",
                    "Segmentation",
                    "Contiguous allocation",
                    "Dynamic partitioning"
                ],
                "correct_answer": "Paging",
                "explanation": "Paging divides memory into fixed-size blocks, preventing external fragmentation."
            },
            {
                "question": "What is the purpose of a file system?",
                "options": [
                    "To organize and store data persistently",
                    "To manage network connections",
                    "To control hardware devices",
                    "To handle user authentication"
                ],
                "correct_answer": "To organize and store data persistently",
                "explanation": "File systems organize and store data persistently on storage devices."
            },
            {
                "question": "Which process state indicates a process is waiting for I/O?",
                "options": [
                    "Blocked/Waiting",
                    "Ready",
                    "Running",
                    "Terminated"
                ],
                "correct_answer": "Blocked/Waiting",
                "explanation": "A process in blocked/waiting state is waiting for I/O operations to complete."
            },
            {
                "question": "What is the main advantage of multiprogramming?",
                "options": [
                    "Increased CPU utilization",
                    "Faster execution of programs",
                    "Reduced memory usage",
                    "Better user interface"
                ],
                "correct_answer": "Increased CPU utilization",
                "explanation": "Multiprogramming increases CPU utilization by keeping multiple programs in memory."
            },
            {
                "question": "Which synchronization mechanism prevents race conditions?",
                "options": [
                    "Mutex (Mutual Exclusion)",
                    "Semaphore",
                    "Monitor",
                    "All of the above"
                ],
                "correct_answer": "All of the above",
                "explanation": "Mutex, semaphore, and monitor are all synchronization mechanisms that prevent race conditions."
            },
            {
                "question": "What is the purpose of a device driver?",
                "options": [
                    "To provide interface between OS and hardware",
                    "To manage user accounts",
                    "To control network traffic",
                    "To handle file operations"
                ],
                "correct_answer": "To provide interface between OS and hardware",
                "explanation": "Device drivers provide an interface between the operating system and hardware devices."
            },
            {
                "question": "Which memory allocation strategy is best for variable-sized processes?",
                "options": [
                    "Dynamic partitioning",
                    "Fixed partitioning",
                    "Paging",
                    "Segmentation"
                ],
                "correct_answer": "Dynamic partitioning",
                "explanation": "Dynamic partitioning allocates memory based on the actual size of processes."
            }
        ]
        
        # Select questions based on topics and number requested
        for i in range(min(num_questions, len(os_questions))):
            q = os_questions[i]
            questions.append({
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "concept": f"Operating System {unit}",
                "question_type": "mcq",
                "difficulty": difficulty,
                "explanation": q["explanation"]
            })
        
        return questions
    
    def _generate_se_fallback_questions(self, unit: str, topics: List[str], num_questions: int, difficulty: str) -> List[Dict]:
        """Generate Software Engineering specific fallback questions"""
        questions = []
        
        # SE-specific question bank
        se_questions = [
            {
                "question": "What is the first phase of the Software Development Life Cycle (SDLC)?",
                "options": [
                    "Requirements Analysis",
                    "Design",
                    "Implementation",
                    "Testing"
                ],
                "correct_answer": "Requirements Analysis",
                "explanation": "Requirements analysis is the first phase where we gather and analyze user requirements."
            },
            {
                "question": "Which software development model is most suitable for projects with unclear requirements?",
                "options": [
                    "Agile/Scrum",
                    "Waterfall",
                    "Spiral",
                    "V-Model"
                ],
                "correct_answer": "Agile/Scrum",
                "explanation": "Agile/Scrum is best for projects with unclear or changing requirements."
            },
            {
                "question": "What is the purpose of UML diagrams in software engineering?",
                "options": [
                    "To visualize and document software design",
                    "To write code automatically",
                    "To test software",
                    "To deploy applications"
                ],
                "correct_answer": "To visualize and document software design",
                "explanation": "UML diagrams help visualize and document software design and architecture."
            },
            {
                "question": "Which testing technique focuses on testing individual components?",
                "options": [
                    "Unit Testing",
                    "Integration Testing",
                    "System Testing",
                    "Acceptance Testing"
                ],
                "correct_answer": "Unit Testing",
                "explanation": "Unit testing focuses on testing individual components or units of code."
            },
            {
                "question": "What is the main goal of software maintenance?",
                "options": [
                    "To keep software operational and up-to-date",
                    "To add new features only",
                    "To fix bugs only",
                    "To improve performance only"
                ],
                "correct_answer": "To keep software operational and up-to-date",
                "explanation": "Software maintenance aims to keep software operational, up-to-date, and meeting user needs."
            }
        ]
        
        # Select questions based on topics and number requested
        for i in range(min(num_questions, len(se_questions))):
            q = se_questions[i]
            questions.append({
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "concept": f"Software Engineering {unit}",
                "question_type": "mcq",
                "difficulty": difficulty,
                "explanation": q["explanation"]
            })
        
        return questions
    
    def _generate_da_fallback_questions(self, unit: str, topics: List[str], num_questions: int, difficulty: str) -> List[Dict]:
        """Generate Data Analytics specific fallback questions"""
        questions = []
        
        # DA-specific question bank
        da_questions = [
            {
                "question": "What is the primary goal of data analytics?",
                "options": [
                    "To extract meaningful insights from data",
                    "To store large amounts of data",
                    "To create databases",
                    "To write code"
                ],
                "correct_answer": "To extract meaningful insights from data",
                "explanation": "Data analytics aims to extract meaningful insights and patterns from data."
            },
            {
                "question": "Which statistical measure indicates the central tendency of data?",
                "options": [
                    "Mean, Median, Mode",
                    "Standard Deviation",
                    "Variance",
                    "Range"
                ],
                "correct_answer": "Mean, Median, Mode",
                "explanation": "Mean, median, and mode are measures of central tendency that indicate the center of data distribution."
            },
            {
                "question": "What is the purpose of data visualization?",
                "options": [
                    "To present data in graphical format for better understanding",
                    "To store data efficiently",
                    "To clean data",
                    "To analyze data statistically"
                ],
                "correct_answer": "To present data in graphical format for better understanding",
                "explanation": "Data visualization presents data in graphical format to make it easier to understand and interpret."
            },
            {
                "question": "Which type of data analysis focuses on predicting future outcomes?",
                "options": [
                    "Predictive Analytics",
                    "Descriptive Analytics",
                    "Diagnostic Analytics",
                    "Prescriptive Analytics"
                ],
                "correct_answer": "Predictive Analytics",
                "explanation": "Predictive analytics focuses on predicting future outcomes based on historical data."
            },
            {
                "question": "What is the main advantage of using machine learning in data analytics?",
                "options": [
                    "To automatically identify patterns in data",
                    "To store data faster",
                    "To create reports",
                    "To visualize data"
                ],
                "correct_answer": "To automatically identify patterns in data",
                "explanation": "Machine learning can automatically identify patterns and relationships in large datasets."
            }
        ]
        
        # Select questions based on topics and number requested
        for i in range(min(num_questions, len(da_questions))):
            q = da_questions[i]
            questions.append({
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "concept": f"Data Analytics {unit}",
                "question_type": "mcq",
                "difficulty": difficulty,
                "explanation": q["explanation"]
            })
        
        return questions
    
    def _generate_generic_fallback_questions(self, subject: str, unit: str, topics: List[str], num_questions: int, difficulty: str) -> List[Dict]:
        """Generate generic fallback questions for any subject"""
        questions = []
        
        for i in range(num_questions):
            topic = topics[i % len(topics)] if topics else f"{subject} {unit}"
            
            question_data = {
                "id": i + 1,
                "question": f"What is the primary purpose of {topic} in {subject}?",
                "options": [
                    f"To manage and optimize {topic} processes",
                    f"To ignore {topic} completely",
                    f"To avoid {topic} implementation",
                    f"To simplify {topic} unnecessarily"
                ],
                "correct_answer": f"To manage and optimize {topic} processes",
                "concept": topic,
                "question_type": "mcq",
                "difficulty": difficulty,
                "explanation": f"The primary purpose of {topic} is to manage and optimize related processes effectively."
            }
            
            questions.append(question_data)
        
        return questions 