#!/usr/bin/env python3
"""
Test script for the Enhanced Report Generator
Tests all features including charts, styling, and report generation
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from enhanced_report_generator import EnhancedReportGenerator
    print("✅ Enhanced Report Generator imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Enhanced Report Generator: {e}")
    sys.exit(1)

def create_sample_evaluation_data():
    """Create sample evaluation data for testing"""
    return {
        'score': 75.0,
        'total_questions': 20,
        'correct_answers': 15,
        'feedback': 'Good performance with room for improvement',
        'original_questions': [
            {
                'id': '1',
                'question': 'What is the primary function of an operating system?',
                'concept': 'Operating System Basics',
                'type': 'multiple_choice',
                'options': ['Data storage', 'Resource management', 'Web browsing', 'File compression'],
                'correct_answer': 'Resource management',
                'explanation': 'Operating systems primarily manage hardware resources like CPU, memory, and I/O devices.'
            },
            {
                'id': '2',
                'question': 'Which scheduling algorithm provides the shortest average waiting time?',
                'concept': 'Process Scheduling',
                'type': 'multiple_choice',
                'options': ['FCFS', 'SJF', 'Round Robin', 'Priority'],
                'correct_answer': 'SJF',
                'explanation': 'Shortest Job First (SJF) provides the minimum average waiting time among all scheduling algorithms.'
            },
            {
                'id': '3',
                'question': 'What is virtual memory?',
                'concept': 'Memory Management',
                'type': 'multiple_choice',
                'options': ['Physical RAM', 'Storage on hard disk', 'Memory management technique', 'Cache memory'],
                'correct_answer': 'Memory management technique',
                'explanation': 'Virtual memory is a memory management technique that uses both RAM and disk storage.'
            },
            {
                'id': '4',
                'question': 'Deadlock occurs when processes are waiting for resources held by other processes.',
                'concept': 'Deadlock',
                'type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer': 'True',
                'explanation': 'Deadlock is a situation where two or more processes are waiting for resources held by each other.'
            },
            {
                'id': '5',
                'question': 'Which of the following is NOT a file system?',
                'concept': 'File Systems',
                'type': 'multiple_choice',
                'options': ['NTFS', 'FAT32', 'ext4', 'TCP/IP'],
                'correct_answer': 'TCP/IP',
                'explanation': 'TCP/IP is a networking protocol, not a file system. NTFS, FAT32, and ext4 are file systems.'
            }
        ],
        'user_answers': {
            '1': 'Resource management',
            '2': 'FCFS',
            '3': 'Memory management technique',
            '4': 'True',
            '5': 'FAT32'
        },
        'mistakes': [
            {
                'question_number': 2,
                'question': 'Which scheduling algorithm provides the shortest average waiting time?',
                'concept': 'Process Scheduling',
                'user_answer': 'FCFS',
                'correct_answer': 'SJF',
                'explanation': 'You selected FCFS (First Come First Serve) instead of SJF (Shortest Job First). SJF provides the minimum average waiting time because it prioritizes shorter jobs.',
                'study_resources': [
                    {
                        'title': 'Process Scheduling Algorithms',
                        'url': 'https://www.geeksforgeeks.org/process-scheduling-algorithms/',
                        'type': 'Article',
                        'description': 'Comprehensive guide to different process scheduling algorithms',
                        'source': 'GeeksforGeeks'
                    },
                    {
                        'title': 'SJF vs FCFS Comparison',
                        'url': 'https://www.tutorialspoint.com/sjf-vs-fcfs',
                        'type': 'Tutorial',
                        'description': 'Detailed comparison between SJF and FCFS scheduling',
                        'source': 'TutorialsPoint'
                    }
                ]
            },
            {
                'question_number': 5,
                'question': 'Which of the following is NOT a file system?',
                'concept': 'File Systems',
                'user_answer': 'FAT32',
                'correct_answer': 'TCP/IP',
                'explanation': 'You selected FAT32, which is actually a file system. TCP/IP is a networking protocol, not a file system.',
                'study_resources': [
                    {
                        'title': 'File System Types',
                        'url': 'https://www.geeksforgeeks.org/file-systems-in-operating-system/',
                        'type': 'Article',
                        'description': 'Overview of different file system types',
                        'source': 'GeeksforGeeks'
                    },
                    {
                        'title': 'TCP/IP Protocol Suite',
                        'url': 'https://www.tutorialspoint.com/tcp-ip-protocol-suite',
                        'type': 'Tutorial',
                        'description': 'Understanding TCP/IP networking protocols',
                        'source': 'TutorialsPoint'
                    }
                ]
            }
        ],
        'historical_scores': [
            {'date': '2024-01-01', 'score': 65.0},
            {'date': '2024-01-15', 'score': 70.0},
            {'date': '2024-02-01', 'score': 75.0}
        ]
    }

def test_chart_generation():
    """Test chart generation functionality"""
    print("\n🧪 Testing Chart Generation...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        
        # Test chart generation
        charts = generator.generate_charts(evaluation_data)
        
        # Verify charts were generated
        assert 'score_pie' in charts, "Score pie chart should be generated"
        assert 'concept_bar' in charts, "Concept bar chart should be generated"
        assert 'trend_line' in charts, "Trend line chart should be generated"
        
        # Verify charts are base64 encoded
        for chart_name, chart_data in charts.items():
            assert isinstance(chart_data, str), f"{chart_name} should be a string"
            assert len(chart_data) > 0, f"{chart_name} should not be empty"
        
        print("✅ Chart generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Chart generation test failed: {e}")
        return False

def test_style_creation():
    """Test style creation functionality"""
    print("\n🧪 Testing Style Creation...")
    
    try:
        generator = EnhancedReportGenerator()
        styles = generator._create_styles()
        
        # Verify all required styles are created
        required_styles = ['title', 'heading', 'sub_heading', 'body', 'success', 'warning', 'info', 'link']
        for style_name in required_styles:
            assert style_name in styles, f"Style '{style_name}' should be created"
        
        print("✅ Style creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Style creation test failed: {e}")
        return False

def test_cover_page_creation():
    """Test cover page creation"""
    print("\n🧪 Testing Cover Page Creation...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        styles = generator._create_styles()
        
        # Test cover page creation
        cover_page = generator._create_cover_page("Operating Systems", "Unit 1", evaluation_data, styles)
        
        # Verify cover page has content
        assert len(cover_page) > 0, "Cover page should have content"
        
        print("✅ Cover page creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Cover page creation test failed: {e}")
        return False

def test_mistake_analysis():
    """Test mistake analysis creation"""
    print("\n🧪 Testing Mistake Analysis...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        styles = generator._create_styles()
        
        # Test mistake analysis creation
        mistake_analysis = generator._create_mistake_analysis(evaluation_data, styles)
        
        # Verify mistake analysis has content
        assert len(mistake_analysis) > 0, "Mistake analysis should have content"
        
        print("✅ Mistake analysis test passed")
        return True
        
    except Exception as e:
        print(f"❌ Mistake analysis test failed: {e}")
        return False

def test_question_review():
    """Test question review creation"""
    print("\n🧪 Testing Question Review...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        styles = generator._create_styles()
        
        # Test question review creation
        question_review = generator._create_question_review(evaluation_data, styles)
        
        # Verify question review has content
        assert len(question_review) > 0, "Question review should have content"
        
        print("✅ Question review test passed")
        return True
        
    except Exception as e:
        print(f"❌ Question review test failed: {e}")
        return False

def test_study_resources():
    """Test study resources creation"""
    print("\n🧪 Testing Study Resources...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        styles = generator._create_styles()
        
        # Test study resources creation
        study_resources = generator._create_study_resources(evaluation_data, styles)
        
        # Verify study resources has content
        assert len(study_resources) > 0, "Study resources should have content"
        
        print("✅ Study resources test passed")
        return True
        
    except Exception as e:
        print(f"❌ Study resources test failed: {e}")
        return False

def test_action_plan():
    """Test action plan creation"""
    print("\n🧪 Testing Action Plan...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        styles = generator._create_styles()
        
        # Test action plan creation
        action_plan = generator._create_action_plan(evaluation_data, styles)
        
        # Verify action plan has content
        assert len(action_plan) > 0, "Action plan should have content"
        
        print("✅ Action plan test passed")
        return True
        
    except Exception as e:
        print(f"❌ Action plan test failed: {e}")
        return False

def test_summary():
    """Test summary creation"""
    print("\n🧪 Testing Summary...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        styles = generator._create_styles()
        
        # Test summary creation
        summary = generator._create_summary(evaluation_data, styles)
        
        # Verify summary has content
        assert len(summary) > 0, "Summary should have content"
        
        print("✅ Summary test passed")
        return True
        
    except Exception as e:
        print(f"❌ Summary test failed: {e}")
        return False

def test_full_report_generation():
    """Test complete report generation"""
    print("\n🧪 Testing Full Report Generation...")
    
    try:
        generator = EnhancedReportGenerator()
        evaluation_data = create_sample_evaluation_data()
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = os.path.join(temp_dir, 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate report
            report_filename = generator.generate_enhanced_report(
                "Operating Systems", 
                "Unit 1", 
                evaluation_data, 
                reports_dir
            )
            
            # Verify report file was created
            report_path = os.path.join(reports_dir, report_filename)
            assert os.path.exists(report_path), f"Report file should be created at {report_path}"
            
            # Verify file size is reasonable (not empty)
            file_size = os.path.getsize(report_path)
            assert file_size > 1000, f"Report file should have reasonable size, got {file_size} bytes"
            
            print(f"✅ Full report generation test passed - File: {report_filename} ({file_size} bytes)")
            return True
            
    except Exception as e:
        print(f"❌ Full report generation test failed: {e}")
        return False

def test_review_tip_generation():
    """Test review tip generation"""
    print("\n🧪 Testing Review Tip Generation...")
    
    try:
        generator = EnhancedReportGenerator()
        
        # Test review tip generation
        mistake = {
            'concept': 'Process Scheduling',
            'user_answer': 'FCFS',
            'correct_answer': 'SJF'
        }
        
        review_tip = generator._generate_review_tip(mistake)
        
        # Verify review tip is generated
        assert isinstance(review_tip, str), "Review tip should be a string"
        assert len(review_tip) > 0, "Review tip should not be empty"
        assert 'FCFS' in review_tip or 'SJF' in review_tip, "Review tip should mention the answers"
        
        print("✅ Review tip generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Review tip generation test failed: {e}")
        return False

def test_performance_levels():
    """Test different performance levels"""
    print("\n🧪 Testing Performance Levels...")
    
    try:
        generator = EnhancedReportGenerator()
        styles = generator._create_styles()
        
        # Test different score levels
        test_scores = [95, 80, 65, 45]
        
        for score in test_scores:
            evaluation_data = create_sample_evaluation_data()
            evaluation_data['score'] = score
            evaluation_data['correct_answers'] = int((score / 100) * evaluation_data['total_questions'])
            
            # Test summary creation with different scores
            summary = generator._create_summary(evaluation_data, styles)
            assert len(summary) > 0, f"Summary should be created for score {score}"
        
        print("✅ Performance levels test passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance levels test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Report Generator Tests")
    print("=" * 50)
    
    tests = [
        test_chart_generation,
        test_style_creation,
        test_cover_page_creation,
        test_mistake_analysis,
        test_question_review,
        test_study_resources,
        test_action_plan,
        test_summary,
        test_review_tip_generation,
        test_performance_levels,
        test_full_report_generation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Enhanced Report Generator is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 