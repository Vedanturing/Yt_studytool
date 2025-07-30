import os
import json
import logging
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, ListFlowable, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ReportLab Graphics imports for charts
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend

import re # Import re for URL slug generation

# Configure logging for this module
logger = logging.getLogger(__name__)

# Custom canvas for page numbers and footer
class _QuizReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page_num, page in enumerate(self.pages):
            self.__dict__.update(page)
            self.draw_page_footer(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_footer(self, page_num, num_pages):
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#555555'))
        self.drawString(inch, 0.75 * inch, f"Page {page_num} of {num_pages}")
        self.restoreState()

# Helper function to generate a URL-friendly slug
def _generate_url_slug(text: str) -> str:
    text = text.lower()
    # Replace non-alphanumeric characters (except hyphens) with empty string
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    return text.strip('-')

class ReportGenerator:
    def generate_report_pdf(self, subject: str, unit: str, evaluation_result: dict, reports_dir: str):
        report_filename = f"{subject.replace(' ', '_')}_{unit.replace(' ', '_')}_report.pdf"
        report_filepath = os.path.join(reports_dir, report_filename)
        print(f"🔍 ReportGenerator: Creating report at {report_filepath}")
        
        doc = SimpleDocTemplate(report_filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Custom styles with colors and improved formatting
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['h1'],
            alignment=TA_CENTER,
            fontSize=32,
            leading=36,
            spaceAfter=40,
            textColor=colors.HexColor('#1A2B3C'),
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['h2'],
            alignment=TA_LEFT,
            fontSize=20,
            leading=24,
            spaceAfter=20,
            spaceBefore=30,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold'
        )
        
        sub_heading_style = ParagraphStyle(
            'SubHeadingStyle',
            parent=styles['h3'],
            alignment=TA_LEFT,
            fontSize=16,
            leading=18,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#2980B9'),
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=12,
            leading=16,
            spaceAfter=8,
            textColor=colors.HexColor('#34495E')
        )

        # Style for mistake details
        mistake_detail_style = ParagraphStyle(
            'MistakeDetailStyle',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            spaceAfter=4,
            leftIndent=20,
            textColor=colors.HexColor('#555555')
        )

        # Style for clickable links
        link_style = ParagraphStyle(
            'LinkStyle',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            textColor=colors.blue,
            underline=1
        )

        # Style for table headers
        table_header_style = ParagraphStyle(
            'TableHeaderStyle',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#FFFFFF'),
            fontName='Helvetica-Bold'
        )

        # --- Report Title Page ---
        report_generation_time = datetime.now()
        story.append(Paragraph("Study Report", title_style))
        story.append(Spacer(1, 0.8 * inch))
        story.append(Paragraph(f"Subject: <b>{subject}</b>", body_style))
        story.append(Paragraph(f"Unit: <b>{unit}</b>", body_style))
        story.append(Paragraph(f"Generated On: {report_generation_time.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
        story.append(Spacer(1, 0.6 * inch))
        
        # Add more content to fill the title page
        story.append(Paragraph("Report Overview", sub_heading_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("This comprehensive study report provides detailed analysis of your quiz performance, including:", body_style))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("• Question-by-question analysis with explanations", body_style))
        story.append(Paragraph("• Performance metrics and concept mastery assessment", body_style))
        story.append(Paragraph("• Visual charts and graphs for better understanding", body_style))
        story.append(Paragraph("• Detailed mistake analysis with study resources", body_style))
        story.append(Paragraph("• Personalized recommendations for improvement", body_style))
        story.append(Paragraph("• Comprehensive action plan for continued learning", body_style))
        story.append(Spacer(1, 0.4 * inch))
        
        # Add performance summary on title page
        total_questions = evaluation_result.get('total_questions', 0)
        correct_answers = evaluation_result.get('correct_answers', 0)
        score = evaluation_result.get('score', 0)
        mistakes_count = len(evaluation_result.get('mistakes', []))
        
        story.append(Paragraph("Quick Performance Summary", sub_heading_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"<b>Total Questions:</b> {total_questions}", body_style))
        story.append(Paragraph(f"<b>Correct Answers:</b> {correct_answers}", body_style))
        story.append(Paragraph(f"<b>Score:</b> {score:.1f}%", body_style))
        story.append(Paragraph(f"<b>Mistakes:</b> {mistakes_count}", body_style))
        story.append(Spacer(1, 0.4 * inch))
        
        # Add page outline for title page
        story.append(Paragraph('<bookmark name="title_page" title="Title Page"/>', body_style))
        story.append(PageBreak())
        
        # Add page outline for evaluation summary
        story.append(Paragraph('<bookmark name="evaluation_summary" title="Evaluation Summary"/>', body_style))
        
        # Evaluation Summary
        story.append(Paragraph("Evaluation Summary", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"Score: <b>{evaluation_result.get('score', 0):.1f}%</b>", body_style))
        story.append(Paragraph(f"Correct Answers: <b>{evaluation_result.get('correct_answers', 0)} / {evaluation_result.get('total_questions', 0)}</b>", body_style))
        story.append(Paragraph(f"Feedback: <i>{evaluation_result.get('feedback', 'N/A')}</i>", body_style))

        # Add multiple charts for quiz performance
        story.append(Spacer(1, 0.6 * inch))
        
        # Create a drawing with multiple charts
        drawing = Drawing(500, 300)
        
        # Pie Chart for Score Distribution
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 150
        pie.height = 150
        pie.data = [evaluation_result.get('correct_answers', 0), evaluation_result.get('total_questions', 0) - evaluation_result.get('correct_answers', 0)]
        pie.labels = ['Correct', 'Incorrect']
        pie.slices.strokeWidth = 2
        pie.slices[0].fillColor = colors.HexColor('#28A745')
        pie.slices[1].fillColor = colors.HexColor('#DC3545')
        drawing.add(pie)
        drawing.add(String(125, 220, 'Score Distribution', textAnchor='middle', fontSize=12, fontName='Helvetica-Bold'))
        
        # Bar Chart for Performance Comparison
        bc = VerticalBarChart()
        bc.x = 250
        bc.y = 50
        bc.height = 150
        bc.width = 200
        bc.data = [
            (evaluation_result.get('correct_answers', 0),),
            (evaluation_result.get('total_questions', 0) - evaluation_result.get('correct_answers', 0),)
        ]
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = evaluation_result.get('total_questions', 0)
        bc.valueAxis.valueStep = 1
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.categoryNames = ['Correct', 'Incorrect']
        bc.bars[0].fillColor = colors.HexColor('#28A745')
        bc.bars[1].fillColor = colors.HexColor('#DC3545')
        drawing.add(bc)
        drawing.add(String(350, 220, 'Performance Comparison', textAnchor='middle', fontSize=12, fontName='Helvetica-Bold'))
        
        story.append(drawing)
        story.append(Spacer(1, 0.6 * inch))
        
        # Add page outline for quiz questions overview
        story.append(Paragraph('<bookmark name="quiz_overview" title="Quiz Questions Overview"/>', body_style))
        
        # Quiz Questions Overview
        story.append(Paragraph("Quiz Questions Overview", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        
        quiz_data = []
        quiz_data.append([Paragraph("<b>#</b>", table_header_style), Paragraph("<b>Question</b>", table_header_style), Paragraph("<b>Concept</b>", table_header_style), Paragraph("<b>Type</b>", table_header_style)])
        
        original_questions = evaluation_result.get('original_questions', [])
        if original_questions:
            print(f"🔍 ReportGenerator: Found {len(original_questions)} questions for table")
            for i, question in enumerate(original_questions):
                question_text = question.get('question', 'N/A')
                concept = question.get('concept', 'N/A')
                question_type = question.get('type', 'N/A')
                
                # Truncate long question text to fit in table
                if len(question_text) > 80:
                    question_text = question_text[:77] + "..."
                
                quiz_data.append([
                    str(i + 1), 
                    Paragraph(question_text, body_style), 
                    Paragraph(concept, body_style), 
                    Paragraph(question_type, body_style)
                ])
        else:
            print(f"🔍 ReportGenerator: No original_questions found in evaluation_result")
            print(f"🔍 ReportGenerator: Available keys: {list(evaluation_result.keys())}")
            print(f"🔍 ReportGenerator: Evaluation result: {evaluation_result}")
            # Fallback if no questions available
            quiz_data.append([
                "1", 
                Paragraph("No questions available in the evaluation data", body_style), 
                Paragraph("N/A", body_style), 
                Paragraph("N/A", body_style)
            ])

        quiz_table = Table(quiz_data, colWidths=[0.4*inch, 4.5*inch, 1.3*inch, 0.8*inch])
        quiz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#DDDDDD')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#DDDDDD')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(quiz_table)
        story.append(Spacer(1, 0.6 * inch))

        # Add page outline for mistakes and study resources
        story.append(Paragraph('<bookmark name="mistakes_resources" title="Mistakes and Study Resources"/>', body_style))
        
        # Detailed Question-by-Question Analysis
        story.append(Paragraph("Detailed Question-by-Question Analysis", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Get all questions and user answers
        original_questions = evaluation_result.get('original_questions', [])
        user_answers_dict = evaluation_result.get('user_answers', {})
        mistakes = evaluation_result.get('mistakes', [])
        
        # Convert user_answers dictionary to list format for easier processing
        user_answers = []
        if original_questions and user_answers_dict:
            for question in original_questions:
                question_id = str(question.get('id', ''))
                user_answer = user_answers_dict.get(question_id, 'Not answered')
                user_answers.append(user_answer)
        
        # Create a map of question numbers to mistakes for easy lookup
        mistake_map = {}
        for mistake in mistakes:
            question_num = mistake.get('question_number', 0)
            mistake_map[question_num] = mistake
        
        # Analyze each question in detail
        for i, question in enumerate(original_questions):
            question_num = i + 1
            user_answer = user_answers[i] if i < len(user_answers) else "Not answered"
            is_correct = question_num not in mistake_map
            
            # Question header with status indicator
            status_color = "#28A745" if is_correct else "#DC3545"
            status_text = "✓ CORRECT" if is_correct else "✗ INCORRECT"
            
            story.append(Paragraph(f"<b>Question {question_num}:</b> <font color='{status_color}'>{status_text}</font>", sub_heading_style))
            story.append(Spacer(1, 0.1 * inch))
            
            # Question details
            story.append(Paragraph(f"<b>Question:</b> {question.get('question', 'N/A')}", body_style))
            story.append(Paragraph(f"<b>Concept:</b> {question.get('concept', 'N/A')}", body_style))
            story.append(Paragraph(f"<b>Question Type:</b> {question.get('type', 'N/A')}", body_style))
            story.append(Spacer(1, 0.1 * inch))
            
            # Options (if multiple choice)
            if question.get('type') == 'multiple_choice' and 'options' in question:
                story.append(Paragraph("<b>Options:</b>", body_style))
                for j, option in enumerate(question['options']):
                    option_letter = chr(65 + j)  # A, B, C, D...
                    story.append(Paragraph(f"   {option_letter}. {option}", mistake_detail_style))
                story.append(Spacer(1, 0.1 * inch))
            
            # User's answer
            story.append(Paragraph(f"<b>Your Answer:</b> {user_answer}", body_style))
            story.append(Paragraph(f"<b>Correct Answer:</b> {question.get('correct_answer', 'N/A')}", body_style))
            story.append(Spacer(1, 0.15 * inch))
            
            # Detailed explanation
            if is_correct:
                # Explanation for correct answer
                story.append(Paragraph("<b>Explanation (Why Your Answer is Correct):</b>", body_style))
                explanation = question.get('explanation', 'Your answer is correct based on the fundamental principles of this concept.')
                story.append(Paragraph(explanation, mistake_detail_style))
                story.append(Paragraph("• You demonstrated a solid understanding of this concept", mistake_detail_style))
                story.append(Paragraph("• Your reasoning aligns with the core principles", mistake_detail_style))
                story.append(Paragraph("• This shows good comprehension of the topic", mistake_detail_style))
            else:
                # Detailed explanation for incorrect answer
                mistake = mistake_map.get(question_num, {})
                story.append(Paragraph("<b>Explanation (Why Your Answer is Incorrect):</b>", body_style))
                explanation = mistake.get('explanation', 'Your answer is incorrect. The correct answer is based on the fundamental principles of this concept.')
                story.append(Paragraph(explanation, mistake_detail_style))
                story.append(Paragraph("• Review the core concepts related to this topic", mistake_detail_style))
                story.append(Paragraph("• Pay attention to the specific details mentioned in the question", mistake_detail_style))
                story.append(Paragraph("• Consider the context and relationships between concepts", mistake_detail_style))
            
            story.append(Spacer(1, 0.2 * inch))
            
            # Learning points
            story.append(Paragraph("<b>Key Learning Points:</b>", body_style))
            learning_points = question.get('learning_points', [])
            if learning_points:
                for point in learning_points:
                    story.append(Paragraph(f"• {point}", mistake_detail_style))
            else:
                story.append(Paragraph("• Understand the fundamental principles of this concept", mistake_detail_style))
                story.append(Paragraph("• Practice applying this knowledge in different scenarios", mistake_detail_style))
                story.append(Paragraph("• Review related concepts for better understanding", mistake_detail_style))
            
            story.append(Spacer(1, 0.3 * inch))
            
            # Add page break for long questions to maintain readability
            if question_num % 3 == 0 and question_num < len(original_questions):
                story.append(PageBreak())
                story.append(Paragraph('<bookmark name="question_analysis" title="Question Analysis"/>', body_style))
        
        story.append(Spacer(1, 0.6 * inch))
        
        # Mistakes and Recommended Study Resources
        story.append(Paragraph("Mistakes and Recommended Study Resources", heading_style))
        story.append(Spacer(1, 0.3 * inch))

        mistakes = evaluation_result.get('mistakes', [])
        if mistakes:
            # Add comprehensive mistake analysis
            story.append(Paragraph("Mistake Analysis Summary", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Mistake statistics
            total_mistakes = len(mistakes)
            total_questions = evaluation_result.get('total_questions', 0)
            mistake_percentage = (total_mistakes / total_questions) * 100 if total_questions > 0 else 0
            
            story.append(Paragraph(f"<b>Total Mistakes:</b> {total_mistakes} out of {total_questions} questions ({mistake_percentage:.1f}%)", body_style))
            story.append(Paragraph(f"<b>Accuracy Rate:</b> {100 - mistake_percentage:.1f}%", body_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # Concept-wise mistake analysis
            concept_mistakes = {}
            for mistake in mistakes:
                concept = mistake.get('concept', 'Unknown')
                if concept not in concept_mistakes:
                    concept_mistakes[concept] = 0
                concept_mistakes[concept] += 1
            
            if concept_mistakes:
                story.append(Paragraph("Mistakes by Concept:", body_style))
                story.append(Spacer(1, 0.1 * inch))
                for concept, count in concept_mistakes.items():
                    story.append(Paragraph(f"• {concept}: {count} mistake(s)", mistake_detail_style))
                story.append(Spacer(1, 0.3 * inch))
            
            # Detailed mistake breakdown
            story.append(Paragraph("Detailed Mistake Breakdown:", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            
            for i, mistake in enumerate(mistakes):
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(f"<b>Mistake {i+1}:</b> Question {mistake.get('question_number', 'N/A')}", sub_heading_style))
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(f"<b>Question:</b> {mistake.get('question', 'N/A')}", body_style))
                story.append(Paragraph(f"<b>Concept:</b> {mistake.get('concept', 'N/A')}", body_style))
                story.append(Paragraph(f"<b>Your Answer:</b> {mistake.get('user_answer', 'N/A')}", body_style))
                story.append(Paragraph(f"<b>Correct Answer:</b> {mistake.get('correct_answer', 'N/A')}", body_style))
                story.append(Spacer(1, 0.15 * inch))

                story.append(Paragraph("<b>Study Resources:</b>", body_style))
                story.append(Spacer(1, 0.1 * inch))
                for j, resource in enumerate(mistake.get('study_resources', [])):
                    title = resource.get('title', 'N/A')
                    url = resource.get('url', '#')
                    resource_type = resource.get('type', 'N/A')
                    description = resource.get('description', 'N/A')

                    resource_text = f"• <link href=\"{url}\"><u>{title}</u></link> ({resource_type}) - {description}"
                    story.append(Paragraph(resource_text, link_style))
                    story.append(Spacer(1, 0.05 * inch))
                story.append(Spacer(1, 0.3 * inch))
        else:
            story.append(Paragraph("No mistakes recorded for this quiz. Excellent work!", body_style))
            story.append(Spacer(1, 0.6 * inch))
        
        # Add summary section with final chart
        story.append(Paragraph('<bookmark name="summary" title="Summary"/>', body_style))
        story.append(Paragraph("Performance Summary", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Create a summary chart showing overall performance
        summary_drawing = Drawing(400, 250)
        
        # Progress chart showing score as percentage
        progress_pie = Pie()
        progress_pie.x = 100
        progress_pie.y = 50
        progress_pie.width = 200
        progress_pie.height = 200
        score = evaluation_result.get('score', 0)
        progress_pie.data = [score, 100 - score]
        progress_pie.labels = [f'{score:.1f}%', f'{100-score:.1f}%']
        progress_pie.slices.strokeWidth = 3
        progress_pie.slices[0].fillColor = colors.HexColor('#28A745')
        progress_pie.slices[1].fillColor = colors.HexColor('#F8F9FA')
        summary_drawing.add(progress_pie)
        summary_drawing.add(String(200, 270, 'Overall Performance', textAnchor='middle', fontSize=14, fontName='Helvetica-Bold'))
        
        story.append(summary_drawing)
        story.append(Spacer(1, 0.6 * inch))
        
        # Add final summary text
        story.append(Paragraph(f"<b>Final Score:</b> {score:.1f}%", body_style))
        story.append(Paragraph(f"<b>Questions Attempted:</b> {evaluation_result.get('total_questions', 0)}", body_style))
        story.append(Paragraph(f"<b>Correct Answers:</b> {evaluation_result.get('correct_answers', 0)}", body_style))
        story.append(Paragraph(f"<b>Areas for Improvement:</b> {len(evaluation_result.get('mistakes', []))} concepts", body_style))
        story.append(Spacer(1, 0.6 * inch))
        
        # Comprehensive Performance Analysis
        story.append(Paragraph("Comprehensive Performance Analysis", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Performance metrics
        total_questions = evaluation_result.get('total_questions', 0)
        correct_answers = evaluation_result.get('correct_answers', 0)
        mistakes = evaluation_result.get('mistakes', [])
        
        # Calculate detailed metrics
        accuracy_rate = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        mistake_rate = (len(mistakes) / total_questions) * 100 if total_questions > 0 else 0
        
        # Performance level assessment
        if accuracy_rate >= 90:
            performance_level = "Excellent"
            performance_color = "#28A745"
        elif accuracy_rate >= 80:
            performance_level = "Good"
            performance_color = "#17A2B8"
        elif accuracy_rate >= 70:
            performance_level = "Satisfactory"
            performance_color = "#FFC107"
        elif accuracy_rate >= 60:
            performance_level = "Needs Improvement"
            performance_color = "#FD7E14"
        else:
            performance_level = "Requires Significant Work"
            performance_color = "#DC3545"
        
        story.append(Paragraph(f"<b>Performance Level:</b> <font color='{performance_color}'>{performance_level}</font>", body_style))
        story.append(Paragraph(f"<b>Accuracy Rate:</b> {accuracy_rate:.1f}%", body_style))
        story.append(Paragraph(f"<b>Mistake Rate:</b> {mistake_rate:.1f}%", body_style))
        story.append(Paragraph(f"<b>Questions Answered:</b> {total_questions}", body_style))
        story.append(Paragraph(f"<b>Correct Responses:</b> {correct_answers}", body_style))
        story.append(Paragraph(f"<b>Incorrect Responses:</b> {len(mistakes)}", body_style))
        story.append(Spacer(1, 0.4 * inch))
        
        # Learning insights
        story.append(Paragraph("Learning Insights", sub_heading_style))
        story.append(Spacer(1, 0.2 * inch))
        
        if mistakes:
            # Simple learning insights based on mistakes
            story.append(Paragraph("<b>Areas Needing Focus:</b>", body_style))
            mistake_concepts = set()
            for mistake in mistakes:
                concept = mistake.get('concept', 'Unknown')
                mistake_concepts.add(concept)
            
            for concept in mistake_concepts:
                story.append(Paragraph(f"• {concept}", mistake_detail_style))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("<b>Recommendations:</b>", body_style))
            story.append(Paragraph("• Review the concepts where you made mistakes", mistake_detail_style))
            story.append(Paragraph("• Use the provided study resources for each concept", mistake_detail_style))
            story.append(Paragraph("• Practice similar questions to strengthen your understanding", mistake_detail_style))
        else:
            story.append(Paragraph("• You have demonstrated excellent understanding across all concepts", mistake_detail_style))
            story.append(Paragraph("• Your knowledge is comprehensive and well-rounded", mistake_detail_style))
            story.append(Paragraph("• Consider exploring advanced topics in this subject", mistake_detail_style))
        
        story.append(Spacer(1, 0.4 * inch))

        # Add recommendations
        if evaluation_result.get('mistakes'):
            story.append(Paragraph("Recommendations for Improvement:", heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• Review the concepts where you made mistakes", body_style))
            story.append(Paragraph("• Use the provided study resources for each concept", body_style))
            story.append(Paragraph("• Practice similar questions to strengthen your understanding", body_style))
            story.append(Paragraph("• Focus on the areas with the most incorrect answers", body_style))
        else:
            story.append(Paragraph("Excellent Performance!", heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• You have demonstrated strong understanding of all concepts", body_style))
            story.append(Paragraph("• Continue to practice to maintain your knowledge", body_style))
            story.append(Paragraph("• Consider exploring advanced topics in this subject", body_style))
        
        # Enhanced recommendations section
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("Detailed Action Plan", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        
        if mistakes:
            # Immediate actions (next 24-48 hours)
            story.append(Paragraph("Immediate Actions (Next 24-48 Hours):", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• Review each incorrect answer and understand why it was wrong", mistake_detail_style))
            story.append(Paragraph("• Read through the provided study resources for weak concepts", mistake_detail_style))
            story.append(Paragraph("• Create flashcards for key concepts you struggled with", mistake_detail_style))
            story.append(Paragraph("• Practice similar questions to reinforce learning", mistake_detail_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # Short-term goals (1-2 weeks)
            story.append(Paragraph("Short-term Goals (1-2 Weeks):", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• Master the concepts where you made mistakes", mistake_detail_style))
            story.append(Paragraph("• Take another quiz on the same topics to measure improvement", mistake_detail_style))
            story.append(Paragraph("• Create a study schedule focusing on weak areas", mistake_detail_style))
            story.append(Paragraph("• Seek additional resources if needed (tutorials, videos, practice problems)", mistake_detail_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # Long-term strategies
            story.append(Paragraph("Long-term Learning Strategies:", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• Regular review sessions to maintain knowledge", mistake_detail_style))
            story.append(Paragraph("• Apply concepts to real-world scenarios", mistake_detail_style))
            story.append(Paragraph("• Teach others to reinforce your understanding", mistake_detail_style))
            story.append(Paragraph("• Stay updated with current developments in the field", mistake_detail_style))
        else:
            # For perfect performance
            story.append(Paragraph("Maintaining Excellence:", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• Continue regular practice to maintain your high level", mistake_detail_style))
            story.append(Paragraph("• Explore advanced topics and challenging problems", mistake_detail_style))
            story.append(Paragraph("• Help others learn by explaining concepts", mistake_detail_style))
            story.append(Paragraph("• Consider taking more advanced courses in this subject", mistake_detail_style))
            story.append(Spacer(1, 0.3 * inch))
            
            story.append(Paragraph("Next Steps for Growth:", sub_heading_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("• Challenge yourself with more complex problems", mistake_detail_style))
            story.append(Paragraph("• Explore related subjects and interdisciplinary connections", mistake_detail_style))
            story.append(Paragraph("• Consider pursuing advanced certifications or courses", mistake_detail_style))
            story.append(Paragraph("• Share your knowledge through teaching or mentoring", mistake_detail_style))
        
        story.append(Spacer(1, 0.6 * inch))
        
        # Study resources summary
        story.append(Paragraph("Study Resources Summary", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Collect all unique study resources
        all_resources = []
        for mistake in mistakes:
            for resource in mistake.get('study_resources', []):
                if resource not in all_resources:
                    all_resources.append(resource)
        
        if all_resources:
            story.append(Paragraph("Recommended Study Materials:", body_style))
            story.append(Spacer(1, 0.2 * inch))
            
            for i, resource in enumerate(all_resources, 1):
                title = resource.get('title', 'N/A')
                url = resource.get('url', '#')
                resource_type = resource.get('type', 'N/A')
                description = resource.get('description', 'N/A')
                
                story.append(Paragraph(f"<b>{i}. {title}</b> ({resource_type})", body_style))
                story.append(Paragraph(f"   <link href=\"{url}\"><u>Access Resource</u></link>", link_style))
                story.append(Paragraph(f"   {description}", mistake_detail_style))
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("No specific study resources available. Focus on reviewing the core concepts and textbook materials.", body_style))
        
        story.append(Spacer(1, 0.6 * inch))

        doc.build(story, canvasmaker=_QuizReportCanvas)

        # Removed the problematic line: toc.data = doc.canvas._outline

        print(f"🔍 ReportGenerator: Successfully generated report: {report_filename}")
        return report_filename # Return the generated report_filepath 