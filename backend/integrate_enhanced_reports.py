#!/usr/bin/env python3
"""
Integration script for Enhanced Report Generator
Shows how to integrate the enhanced report generator with the existing quiz system
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

try:
    from enhanced_report_generator import EnhancedReportGenerator
    print("✅ Enhanced Report Generator imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Enhanced Report Generator: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedReportIntegration:
    """
    Integration class for using enhanced reports with the existing quiz system
    """
    
    def __init__(self):
        self.report_generator = EnhancedReportGenerator()
        
    def convert_quiz_result_to_evaluation_data(self, quiz_result: Dict) -> Dict:
        """
        Convert quiz result from the existing system to evaluation data format
        """
        try:
            # Extract basic information
            questions = quiz_result.get('questions', [])
            user_answers = quiz_result.get('user_answers', {})
            score = quiz_result.get('score', 0)
            total_questions = len(questions)
            correct_answers = int((score / 100) * total_questions) if score > 0 else 0
            
            # Convert questions to the expected format
            original_questions = []
            for i, question in enumerate(questions):
                original_questions.append({
                    'id': str(i + 1),
                    'question': question.get('question', ''),
                    'concept': question.get('topic', 'General'),
                    'type': question.get('type', 'mcq'),
                    'options': question.get('options', []),
                    'correct_answer': question.get('answer', ''),
                    'explanation': question.get('explanation', '')
                })
            
            # Convert user answers to the expected format
            user_answers_dict = {}
            for i, question in enumerate(questions):
                question_id = str(i + 1)
                user_answer = user_answers.get(question_id, 'Not answered')
                user_answers_dict[question_id] = user_answer
            
            # Identify mistakes
            mistakes = []
            for i, question in enumerate(questions):
                question_id = str(i + 1)
                user_answer = user_answers.get(question_id, 'Not answered')
                correct_answer = question.get('answer', '')
                
                if user_answer != correct_answer:
                    mistake = {
                        'question_number': i + 1,
                        'question': question.get('question', ''),
                        'concept': question.get('topic', 'General'),
                        'user_answer': user_answer,
                        'correct_answer': correct_answer,
                        'explanation': question.get('explanation', ''),
                        'study_resources': self._generate_study_resources(question.get('topic', 'General'))
                    }
                    mistakes.append(mistake)
            
            # Create evaluation data
            evaluation_data = {
                'score': score,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'feedback': self._generate_feedback(score),
                'original_questions': original_questions,
                'user_answers': user_answers_dict,
                'mistakes': mistakes
            }
            
            return evaluation_data
            
        except Exception as e:
            logger.error(f"Error converting quiz result: {e}")
            raise
    
    def _generate_study_resources(self, topic: str) -> List[Dict]:
        """
        Generate study resources for a given topic
        """
        # This is a simplified version - in a real implementation,
        # you would integrate with your web scraper or resource database
        
        resources = {
            'Operating System Basics': [
                {
                    'title': 'Operating System Fundamentals',
                    'url': 'https://www.geeksforgeeks.org/operating-system-fundamentals/',
                    'type': 'Article',
                    'description': 'Comprehensive guide to operating system basics',
                    'source': 'GeeksforGeeks'
                }
            ],
            'Process Scheduling': [
                {
                    'title': 'Process Scheduling Algorithms',
                    'url': 'https://www.geeksforgeeks.org/process-scheduling-algorithms/',
                    'type': 'Article',
                    'description': 'Detailed explanation of different scheduling algorithms',
                    'source': 'GeeksforGeeks'
                }
            ],
            'Memory Management': [
                {
                    'title': 'Memory Management in Operating Systems',
                    'url': 'https://www.geeksforgeeks.org/memory-management-in-operating-system/',
                    'type': 'Article',
                    'description': 'Understanding memory management concepts',
                    'source': 'GeeksforGeeks'
                }
            ],
            'File Systems': [
                {
                    'title': 'File System Types',
                    'url': 'https://www.geeksforgeeks.org/file-systems-in-operating-system/',
                    'type': 'Article',
                    'description': 'Overview of different file system types',
                    'source': 'GeeksforGeeks'
                }
            ]
        }
        
        return resources.get(topic, [
            {
                'title': f'{topic} - General Resources',
                'url': 'https://www.geeksforgeeks.org/',
                'type': 'Article',
                'description': f'General resources for {topic}',
                'source': 'GeeksforGeeks'
            }
        ])
    
    def _generate_feedback(self, score: float) -> str:
        """
        Generate feedback based on score
        """
        if score >= 90:
            return "Excellent performance! You have demonstrated mastery of the concepts."
        elif score >= 80:
            return "Good performance with room for improvement in some areas."
        elif score >= 70:
            return "Satisfactory performance. Focus on weak areas for improvement."
        elif score >= 60:
            return "Needs improvement. Review the concepts thoroughly."
        else:
            return "Requires significant work. Consider seeking additional help."
    
    def generate_enhanced_quiz_report(self, subject: str, unit: str, quiz_result: Dict, reports_dir: str) -> str:
        """
        Generate enhanced report for a quiz result
        """
        try:
            # Convert quiz result to evaluation data
            evaluation_data = self.convert_quiz_result_to_evaluation_data(quiz_result)
            
            # Generate enhanced report
            report_filename = self.report_generator.generate_enhanced_report(
                subject, unit, evaluation_data, reports_dir
            )
            
            logger.info(f"Enhanced report generated: {report_filename}")
            return report_filename
            
        except Exception as e:
            logger.error(f"Error generating enhanced quiz report: {e}")
            raise
    
    def generate_comparison_report(self, subject: str, unit: str, quiz_results: List[Dict], reports_dir: str) -> str:
        """
        Generate a comparison report for multiple quiz attempts
        """
        try:
            # Convert all quiz results to evaluation data
            evaluation_data_list = []
            for quiz_result in quiz_results:
                evaluation_data = self.convert_quiz_result_to_evaluation_data(quiz_result)
                evaluation_data_list.append(evaluation_data)
            
            # Create combined evaluation data
            combined_data = self._combine_evaluation_data(evaluation_data_list)
            
            # Generate enhanced report
            report_filename = self.report_generator.generate_enhanced_report(
                subject, unit, combined_data, reports_dir
            )
            
            logger.info(f"Comparison report generated: {report_filename}")
            return report_filename
            
        except Exception as e:
            logger.error(f"Error generating comparison report: {e}")
            raise
    
    def _combine_evaluation_data(self, evaluation_data_list: List[Dict]) -> Dict:
        """
        Combine multiple evaluation data sets into one
        """
        if not evaluation_data_list:
            raise ValueError("No evaluation data provided")
        
        # Use the first evaluation data as base
        combined = evaluation_data_list[0].copy()
        
        # Calculate average score
        total_score = sum(data.get('score', 0) for data in evaluation_data_list)
        avg_score = total_score / len(evaluation_data_list)
        combined['score'] = avg_score
        
        # Combine all mistakes
        all_mistakes = []
        for data in evaluation_data_list:
            all_mistakes.extend(data.get('mistakes', []))
        combined['mistakes'] = all_mistakes
        
        # Add historical scores
        historical_scores = []
        for i, data in enumerate(evaluation_data_list):
            historical_scores.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'score': data.get('score', 0)
            })
        combined['historical_scores'] = historical_scores
        
        return combined

def create_sample_quiz_result():
    """
    Create a sample quiz result for testing
    """
    return {
        'questions': [
            {
                'question': 'What is the primary function of an operating system?',
                'topic': 'Operating System Basics',
                'type': 'mcq',
                'options': ['Data storage', 'Resource management', 'Web browsing', 'File compression'],
                'answer': 'Resource management',
                'explanation': 'Operating systems primarily manage hardware resources like CPU, memory, and I/O devices.'
            },
            {
                'question': 'Which scheduling algorithm provides the shortest average waiting time?',
                'topic': 'Process Scheduling',
                'type': 'mcq',
                'options': ['FCFS', 'SJF', 'Round Robin', 'Priority'],
                'answer': 'SJF',
                'explanation': 'Shortest Job First (SJF) provides the minimum average waiting time among all scheduling algorithms.'
            },
            {
                'question': 'What is virtual memory?',
                'topic': 'Memory Management',
                'type': 'mcq',
                'options': ['Physical RAM', 'Storage on hard disk', 'Memory management technique', 'Cache memory'],
                'answer': 'Memory management technique',
                'explanation': 'Virtual memory is a memory management technique that uses both RAM and disk storage.'
            }
        ],
        'user_answers': {
            '1': 'Resource management',
            '2': 'FCFS',
            '3': 'Memory management technique'
        },
        'score': 66.67
    }

def main():
    """
    Main function to demonstrate the integration
    """
    print("🚀 Enhanced Report Generator Integration Demo")
    print("=" * 50)
    
    try:
        # Create integration instance
        integration = EnhancedReportIntegration()
        
        # Create sample quiz result
        quiz_result = create_sample_quiz_result()
        
        # Create reports directory
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate enhanced report
        print("\n📊 Generating Enhanced Quiz Report...")
        report_filename = integration.generate_enhanced_quiz_report(
            "Operating Systems",
            "Unit 1",
            quiz_result,
            reports_dir
        )
        
        print(f"✅ Enhanced report generated: {report_filename}")
        print(f"📁 Report location: {os.path.join(reports_dir, report_filename)}")
        
        # Demonstrate conversion
        print("\n🔄 Converting Quiz Result to Evaluation Data...")
        evaluation_data = integration.convert_quiz_result_to_evaluation_data(quiz_result)
        
        print(f"✅ Converted {len(evaluation_data['original_questions'])} questions")
        print(f"✅ Found {len(evaluation_data['mistakes'])} mistakes")
        print(f"✅ Score: {evaluation_data['score']}%")
        
        print("\n🎉 Integration demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 