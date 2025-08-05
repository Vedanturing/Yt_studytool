import os
import json
import logging
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import io
import base64

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, 
    ListFlowable, Table, TableStyle, Frame, PageTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus.flowables import HRFlowable

# Configure matplotlib for better charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedReportGenerator:
    """
    Enhanced PDF Report Generator with improved visuals, charts, and layout
    """
    
    def __init__(self):
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#3498DB', 
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'info': '#17A2B8',
            'light': '#F8F9FA',
            'dark': '#343A40',
            'muted': '#6C757D'
        }
        
        self.fonts = {
            'title': 'Helvetica-Bold',
            'heading': 'Helvetica-Bold', 
            'body': 'Helvetica',
            'code': 'Courier'
        }
        
    def generate_charts(self, evaluation_result: dict) -> Dict[str, str]:
        """
        Generate charts and save as base64 encoded images
        """
        charts = {}
        
        try:
            # Pie chart for score distribution
            charts['score_pie'] = self._create_score_pie_chart(evaluation_result)
            
            # Bar chart for mistakes by concept
            charts['concept_bar'] = self._create_concept_bar_chart(evaluation_result)
            
            # Performance trend (if historical data available)
            if 'historical_scores' in evaluation_result:
                charts['trend_line'] = self._create_trend_chart(evaluation_result)
                
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            
        return charts
    
    def _create_score_pie_chart(self, evaluation_result: dict) -> str:
        """Create pie chart for score distribution"""
        try:
            correct = evaluation_result.get('correct_answers', 0)
            incorrect = evaluation_result.get('total_questions', 0) - correct
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = ['Correct', 'Incorrect']
            sizes = [correct, incorrect]
            colors_chart = [self.colors['success'], self.colors['danger']]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_chart, 
                                             autopct='%1.1f%%', startangle=90)
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Score Distribution', fontsize=16, fontweight='bold', pad=20)
            
            # Save to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            return ""
    
    def _create_concept_bar_chart(self, evaluation_result: dict) -> str:
        """Create bar chart for mistakes by concept"""
        try:
            mistakes = evaluation_result.get('mistakes', [])
            concept_mistakes = {}
            
            for mistake in mistakes:
                concept = mistake.get('concept', 'Unknown')
                concept_mistakes[concept] = concept_mistakes.get(concept, 0) + 1
            
            if not concept_mistakes:
                return ""
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            concepts = list(concept_mistakes.keys())
            counts = list(concept_mistakes.values())
            
            bars = ax.bar(concepts, counts, color=self.colors['warning'])
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title('Mistakes by Concept', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Concepts', fontsize=12)
            ax.set_ylabel('Number of Mistakes', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            return ""
    
    def _create_trend_chart(self, evaluation_result: dict) -> str:
        """Create trend line chart for historical performance"""
        try:
            historical_scores = evaluation_result.get('historical_scores', [])
            if len(historical_scores) < 2:
                return ""
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            dates = [score['date'] for score in historical_scores]
            scores = [score['score'] for score in historical_scores]
            
            ax.plot(dates, scores, marker='o', linewidth=3, markersize=8, 
                   color=self.colors['secondary'])
            
            ax.set_title('Performance Trend', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Score (%)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            logger.error(f"Error creating trend chart: {e}")
            return ""
    
    def _create_styles(self):
        """Create enhanced paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Enhanced title style
        title_style = ParagraphStyle(
            'EnhancedTitle',
            parent=styles['h1'],
            alignment=TA_CENTER,
            fontSize=28,
            leading=32,
            spaceAfter=30,
            textColor=colors.HexColor(self.colors['primary']),
            fontName=self.fonts['title'],
            spaceBefore=20
        )
        
        # Enhanced heading style
        heading_style = ParagraphStyle(
            'EnhancedHeading',
            parent=styles['h2'],
            alignment=TA_LEFT,
            fontSize=18,
            leading=22,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor(self.colors['secondary']),
            fontName=self.fonts['heading'],
            borderWidth=1,
            borderColor=colors.HexColor(self.colors['secondary']),
            borderPadding=8,
            backColor=colors.HexColor(self.colors['light'])
        )
        
        # Sub-heading style
        sub_heading_style = ParagraphStyle(
            'EnhancedSubHeading',
            parent=styles['h3'],
            alignment=TA_LEFT,
            fontSize=14,
            leading=18,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor(self.colors['dark']),
            fontName=self.fonts['heading']
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'EnhancedBody',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY,
            fontSize=11,
            leading=14,
            spaceAfter=6,
            textColor=colors.HexColor(self.colors['dark']),
            fontName=self.fonts['body']
        )
        
        # Success box style
        success_style = ParagraphStyle(
            'SuccessBox',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            spaceAfter=8,
            leftIndent=15,
            rightIndent=15,
            backColor=colors.HexColor('#D4EDDA'),
            borderWidth=1,
            borderColor=colors.HexColor(self.colors['success']),
            borderPadding=8,
            textColor=colors.HexColor('#155724')
        )
        
        # Warning box style
        warning_style = ParagraphStyle(
            'WarningBox',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            spaceAfter=8,
            leftIndent=15,
            rightIndent=15,
            backColor=colors.HexColor('#FFF3CD'),
            borderWidth=1,
            borderColor=colors.HexColor(self.colors['warning']),
            borderPadding=8,
            textColor=colors.HexColor('#856404')
        )
        
        # Info box style
        info_style = ParagraphStyle(
            'InfoBox',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            spaceAfter=8,
            leftIndent=15,
            rightIndent=15,
            backColor=colors.HexColor('#D1ECF1'),
            borderWidth=1,
            borderColor=colors.HexColor(self.colors['info']),
            borderPadding=8,
            textColor=colors.HexColor('#0C5460')
        )
        
        # Link style
        link_style = ParagraphStyle(
            'EnhancedLink',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            textColor=colors.blue,
            fontName=self.fonts['body'],
            underline=1
        )
        
        return {
            'title': title_style,
            'heading': heading_style,
            'sub_heading': sub_heading_style,
            'body': body_style,
            'success': success_style,
            'warning': warning_style,
            'info': info_style,
            'link': link_style
        }
    
    def _create_cover_page(self, subject: str, unit: str, evaluation_result: dict, styles: dict) -> List:
        """Create enhanced cover page"""
        story = []
        
        # Main title
        story.append(Paragraph("📊 AI-Powered Learning Report", styles['title']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Subject and unit info
        story.append(Paragraph(f"<b>Subject:</b> {subject}", styles['body']))
        story.append(Paragraph(f"<b>Unit:</b> {unit}", styles['body']))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['body']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Performance summary box
        score = evaluation_result.get('score', 0)
        total_questions = evaluation_result.get('total_questions', 0)
        correct_answers = evaluation_result.get('correct_answers', 0)
        
        accuracy = (correct_answers/total_questions*100) if total_questions > 0 else 0
        performance_text = f"""
        <b>🎯 Performance Summary</b><br/>
        Score: {score:.1f}%<br/>
        Questions: {total_questions}<br/>
        Correct: {correct_answers}<br/>
        Accuracy: {accuracy:.1f}%
        """
        
        story.append(Paragraph(performance_text, styles['info']))
        story.append(Spacer(1, 0.4 * inch))
        
        # Report overview
        story.append(Paragraph("📋 Report Overview", styles['sub_heading']))
        story.append(Paragraph("This comprehensive report includes:", styles['body']))
        story.append(Paragraph("• 📊 Visual performance charts and graphs", styles['body']))
        story.append(Paragraph("• 🔍 Detailed question-by-question analysis", styles['body']))
        story.append(Paragraph("• ❌ Mistake analysis with explanations", styles['body']))
        story.append(Paragraph("• 📚 Personalized study recommendations", styles['body']))
        story.append(Paragraph("• 🎯 Action plan for improvement", styles['body']))
        story.append(Paragraph("• 🔗 Curated study resources", styles['body']))
        
        story.append(PageBreak())
        return story
    
    def _create_table_of_contents(self, styles: dict) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("📑 Table of Contents", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        toc_items = [
            ("📊 Executive Summary", "executive_summary"),
            ("📈 Performance Analysis", "performance_analysis"),
            ("❌ Mistake Analysis", "mistake_analysis"),
            ("🔍 Question Review", "question_review"),
            ("📚 Study Resources", "study_resources"),
            ("🎯 Action Plan", "action_plan"),
            ("📋 Summary & Recommendations", "summary")
        ]
        
        for title, bookmark in toc_items:
            story.append(Paragraph(f'{title}', styles['link']))
            story.append(Spacer(1, 0.1 * inch))
        
        story.append(PageBreak())
        return story
    
    def _create_executive_summary(self, evaluation_result: dict, charts: dict, styles: dict) -> List:
        """Create executive summary with charts"""
        story = []
        
        story.append(Paragraph('<a name="executive_summary"/>', styles['body']))
        story.append(Paragraph("📊 Executive Summary", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Performance metrics
        score = evaluation_result.get('score', 0)
        total_questions = evaluation_result.get('total_questions', 0)
        correct_answers = evaluation_result.get('correct_answers', 0)
        mistakes = evaluation_result.get('mistakes', [])
        
        # Performance level assessment
        if score >= 90:
            level = "🏆 Excellent"
            level_color = self.colors['success']
        elif score >= 80:
            level = "👍 Good"
            level_color = self.colors['info']
        elif score >= 70:
            level = "⚠️ Satisfactory"
            level_color = self.colors['warning']
        else:
            level = "❌ Needs Improvement"
            level_color = self.colors['danger']
        
        accuracy_rate = (correct_answers/total_questions*100) if total_questions > 0 else 0
        summary_text = f"""
        <b>Performance Level:</b> <font color="{level_color}">{level}</font><br/>
        <b>Overall Score:</b> {score:.1f}%<br/>
        <b>Questions Attempted:</b> {total_questions}<br/>
        <b>Correct Answers:</b> {correct_answers}<br/>
        <b>Mistakes:</b> {len(mistakes)}<br/>
        <b>Accuracy Rate:</b> {accuracy_rate:.1f}%
        """
        
        story.append(Paragraph(summary_text, styles['info']))
        story.append(Spacer(1, 0.4 * inch))
        
        # Add charts if available
        if charts.get('score_pie'):
            story.append(Paragraph("📊 Score Distribution", styles['sub_heading']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Convert base64 to image
            img_data = base64.b64decode(charts['score_pie'])
            img_buffer = io.BytesIO(img_data)
            img = Image(img_buffer, width=4*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        
        if charts.get('concept_bar'):
            story.append(Paragraph("📈 Mistakes by Concept", styles['sub_heading']))
            story.append(Spacer(1, 0.2 * inch))
            
            img_data = base64.b64decode(charts['concept_bar'])
            img_buffer = io.BytesIO(img_data)
            img = Image(img_buffer, width=5*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.3 * inch))
        
        story.append(PageBreak())
        return story
    
    def _create_mistake_analysis(self, evaluation_result: dict, styles: dict) -> List:
        """Create detailed mistake analysis with review tips"""
        story = []
        
        story.append(Paragraph('<a name="mistake_analysis"/>', styles['body']))
        story.append(Paragraph("❌ Mistake Analysis", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        mistakes = evaluation_result.get('mistakes', [])
        
        if not mistakes:
            story.append(Paragraph("🎉 Perfect Score! No mistakes found.", styles['success']))
            story.append(Spacer(1, 0.3 * inch))
            return story
        
        # Mistake statistics
        concept_mistakes = {}
        for mistake in mistakes:
            concept = mistake.get('concept', 'Unknown')
            concept_mistakes[concept] = concept_mistakes.get(concept, 0) + 1
        
        story.append(Paragraph("📊 Mistake Statistics", styles['sub_heading']))
        story.append(Paragraph(f"Total Mistakes: {len(mistakes)}", styles['body']))
        story.append(Paragraph(f"Concepts with Mistakes: {len(concept_mistakes)}", styles['body']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Concept-wise breakdown
        for concept, count in concept_mistakes.items():
            story.append(Paragraph(f"• {concept}: {count} mistake(s)", styles['body']))
        
        story.append(Spacer(1, 0.4 * inch))
        
        # Detailed mistake analysis with review tips
        story.append(Paragraph("🔍 Detailed Analysis with Review Tips", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        for i, mistake in enumerate(mistakes, 1):
            story.append(Paragraph(f"<b>Mistake {i}: Question {mistake.get('question_number', 'N/A')}</b>", styles['sub_heading']))
            story.append(Spacer(1, 0.1 * inch))
            
            # Question details
            story.append(Paragraph(f"<b>Question:</b> {mistake.get('question', 'N/A')}", styles['body']))
            story.append(Paragraph(f"<b>Concept:</b> {mistake.get('concept', 'N/A')}", styles['body']))
            story.append(Paragraph(f"<b>Your Answer:</b> {mistake.get('user_answer', 'N/A')}", styles['body']))
            story.append(Paragraph(f"<b>Correct Answer:</b> {mistake.get('correct_answer', 'N/A')}", styles['body']))
            story.append(Spacer(1, 0.15 * inch))
            
            # Review tip box
            review_tip = self._generate_review_tip(mistake)
            story.append(Paragraph(f"💡 <b>Review Tip:</b><br/>{review_tip}", styles['warning']))
            story.append(Spacer(1, 0.15 * inch))
            
            # Explanation
            story.append(Paragraph("<b>Explanation:</b>", styles['body']))
            explanation = mistake.get('explanation', 'Review the concept thoroughly to understand the correct answer.')
            story.append(Paragraph(explanation, styles['body']))
            story.append(Spacer(1, 0.15 * inch))
            
            # Study resources
            study_resources = mistake.get('study_resources', [])
            if study_resources:
                story.append(Paragraph("<b>📚 Recommended Study Resources:</b>", styles['body']))
                for resource in study_resources:
                    title = resource.get('title', 'N/A')
                    url = resource.get('url', '#')
                    resource_type = resource.get('type', 'N/A')
                    
                    resource_text = f"• <link href='{url}'><u>{title}</u></link> ({resource_type})"
                    story.append(Paragraph(resource_text, styles['link']))
                
                story.append(Spacer(1, 0.1 * inch))
            
            # Source attribution
            if study_resources:
                story.append(Paragraph(f"<i>Source: {study_resources[0].get('source', 'Study Resources')}</i>", styles['body']))
            
            story.append(Spacer(1, 0.3 * inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_review_tip(self, mistake: dict) -> str:
        """Generate personalized review tip for a mistake"""
        concept = mistake.get('concept', 'this concept')
        user_answer = mistake.get('user_answer', 'your answer')
        correct_answer = mistake.get('correct_answer', 'the correct answer')
        
        tips = [
            f"You selected '{user_answer}' instead of '{correct_answer}'. Focus on understanding the key differences between these concepts.",
            f"Review the fundamental principles of {concept} to avoid similar mistakes in the future.",
            f"Pay attention to the specific context and requirements when answering questions about {concept}.",
            f"Practice distinguishing between similar concepts in {concept} to strengthen your understanding.",
            f"Consider the relationships and dependencies within {concept} when selecting your answer."
        ]
        
        import random
        return random.choice(tips)
    
    def _create_question_review(self, evaluation_result: dict, styles: dict) -> List:
        """Create detailed question-by-question review with color coding"""
        story = []
        
        story.append(Paragraph('<a name="question_review"/>', styles['body']))
        story.append(Paragraph("🔍 Question-by-Question Review", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        original_questions = evaluation_result.get('original_questions', [])
        user_answers_dict = evaluation_result.get('user_answers', {})
        mistakes = evaluation_result.get('mistakes', [])
        
        # Create mistake map for quick lookup
        mistake_map = {mistake.get('question_number', 0): mistake for mistake in mistakes}
        
        if not original_questions:
            story.append(Paragraph("No questions available for review.", styles['body']))
            story.append(PageBreak())
            return story
        
        # Create summary table
        story.append(Paragraph("📋 Question Summary Table", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Table headers
        table_data = [
            ['#', 'Question', 'Concept', 'Your Answer', 'Correct Answer', 'Status']
        ]
        
        for i, question in enumerate(original_questions):
            question_num = i + 1
            user_answer = user_answers_dict.get(str(question.get('id', '')), 'Not answered')
            correct_answer = question.get('correct_answer', 'N/A')
            is_correct = question_num not in mistake_map
            
            # Status with emoji
            status = "✅ Correct" if is_correct else "❌ Incorrect"
            
            # Truncate long text
            question_text = question.get('question', 'N/A')
            if len(question_text) > 60:
                question_text = question_text[:57] + "..."
            
            table_data.append([
                str(question_num),
                question_text,
                question.get('concept', 'N/A'),
                user_answer,
                correct_answer,
                status
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
        
        # Table styling
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(self.colors['light'])),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        # Color code correct/incorrect rows
        for i in range(1, len(table_data)):
            if "✅" in table_data[i][-1]:  # Correct
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#D4EDDA'))
            else:  # Incorrect
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8D7DA'))
        
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 0.4 * inch))
        
        # Detailed question analysis
        story.append(Paragraph("📝 Detailed Question Analysis", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        for i, question in enumerate(original_questions):
            question_num = i + 1
            user_answer = user_answers_dict.get(str(question.get('id', '')), 'Not answered')
            is_correct = question_num not in mistake_map
            
            # Question header with status
            status_color = self.colors['success'] if is_correct else self.colors['danger']
            status_text = "✅ CORRECT" if is_correct else "❌ INCORRECT"
            
            story.append(Paragraph(
                f"<b>Question {question_num}:</b> <font color='{status_color}'>{status_text}</font>", 
                styles['sub_heading']
            ))
            story.append(Spacer(1, 0.1 * inch))
            
            # Question details in colored box
            box_style = styles['success'] if is_correct else styles['warning']
            question_details = f"""
            <b>Question:</b> {question.get('question', 'N/A')}<br/>
            <b>Concept:</b> {question.get('concept', 'N/A')}<br/>
            <b>Type:</b> {question.get('type', 'N/A')}<br/>
            <b>Your Answer:</b> {user_answer}<br/>
            <b>Correct Answer:</b> {question.get('correct_answer', 'N/A')}
            """
            story.append(Paragraph(question_details, box_style))
            story.append(Spacer(1, 0.15 * inch))
            
            # Options for multiple choice
            if question.get('type') == 'multiple_choice' and 'options' in question:
                story.append(Paragraph("<b>Options:</b>", styles['body']))
                for j, option in enumerate(question['options']):
                    option_letter = chr(65 + j)
                    story.append(Paragraph(f"   {option_letter}. {option}", styles['body']))
                story.append(Spacer(1, 0.1 * inch))
            
            # Explanation
            if is_correct:
                story.append(Paragraph("<b>✅ Why This is Correct:</b>", styles['body']))
                explanation = question.get('explanation', 'Your answer demonstrates a solid understanding of the concept.')
                story.append(Paragraph(explanation, styles['body']))
            else:
                mistake = mistake_map.get(question_num, {})
                story.append(Paragraph("<b>❌ Why This is Incorrect:</b>", styles['body']))
                explanation = mistake.get('explanation', 'Review the concept to understand the correct answer.')
                story.append(Paragraph(explanation, styles['body']))
            
            story.append(Spacer(1, 0.2 * inch))
            
            # Page break every 3 questions for readability
            if question_num % 3 == 0 and question_num < len(original_questions):
                story.append(PageBreak())
        
        story.append(PageBreak())
        return story
    
    def _create_study_resources(self, evaluation_result: dict, styles: dict) -> List:
        """Create comprehensive study resources section"""
        story = []
        
        story.append(Paragraph('<a name="study_resources"/>', styles['body']))
        story.append(Paragraph("📚 Study Resources & Recommendations", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        mistakes = evaluation_result.get('mistakes', [])
        
        if not mistakes:
            story.append(Paragraph("🎉 Excellent performance! Here are some advanced resources to further your knowledge:", styles['success']))
            story.append(Spacer(1, 0.2 * inch))
            
            # General advanced resources
            story.append(Paragraph("🚀 Advanced Learning Resources", styles['sub_heading']))
            story.append(Paragraph("• Explore advanced topics in your subject area", styles['body']))
            story.append(Paragraph("• Practice with more challenging problems", styles['body']))
            story.append(Paragraph("• Consider pursuing certifications or advanced courses", styles['body']))
            story.append(Spacer(1, 0.3 * inch))
        else:
            # Collect all study resources from mistakes
            all_resources = []
            concept_resources = {}
            
            for mistake in mistakes:
                concept = mistake.get('concept', 'Unknown')
                resources = mistake.get('study_resources', [])
                
                if concept not in concept_resources:
                    concept_resources[concept] = []
                
                for resource in resources:
                    if resource not in concept_resources[concept]:
                        concept_resources[concept].append(resource)
                    if resource not in all_resources:
                        all_resources.append(resource)
            
            # Concept-wise resources
            story.append(Paragraph("🎯 Resources by Concept", styles['sub_heading']))
            story.append(Spacer(1, 0.2 * inch))
            
            for concept, resources in concept_resources.items():
                story.append(Paragraph(f"<b>{concept}</b>", styles['sub_heading']))
                story.append(Spacer(1, 0.1 * inch))
                
                for resource in resources:
                    title = resource.get('title', 'N/A')
                    url = resource.get('url', '#')
                    resource_type = resource.get('type', 'N/A')
                    description = resource.get('description', 'N/A')
                    source = resource.get('source', 'Study Resource')
                    
                    resource_text = f"""
                    <b>📖 {title}</b> ({resource_type})<br/>
                    <link href='{url}'><u>🔗 Access Resource</u></link><br/>
                    {description}<br/>
                    <i>Source: {source}</i>
                    """
                    story.append(Paragraph(resource_text, styles['info']))
                    story.append(Spacer(1, 0.1 * inch))
                
                story.append(Spacer(1, 0.2 * inch))
            
            # General study tips
            story.append(Paragraph("💡 General Study Tips", styles['sub_heading']))
            story.append(Spacer(1, 0.2 * inch))
            
            tips = [
                "Review concepts where you made mistakes thoroughly",
                "Practice with similar questions to reinforce learning",
                "Create flashcards for key concepts",
                "Use spaced repetition techniques",
                "Teach others to solidify your understanding",
                "Take regular breaks during study sessions",
                "Use multiple learning resources for different perspectives"
            ]
            
            for tip in tips:
                story.append(Paragraph(f"• {tip}", styles['body']))
            
            story.append(Spacer(1, 0.3 * inch))
        
        # Recommended study schedule
        story.append(Paragraph("📅 Recommended Study Schedule", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        schedule_text = """
        <b>Immediate (Next 24-48 hours):</b><br/>
        • Review all incorrect answers and explanations<br/>
        • Read through recommended study resources<br/>
        • Create summary notes for weak concepts<br/><br/>
        
        <b>Short-term (1-2 weeks):</b><br/>
        • Practice with similar questions<br/>
        • Take another quiz to measure improvement<br/>
        • Focus on concepts with multiple mistakes<br/><br/>
        
        <b>Long-term (Ongoing):</b><br/>
        • Regular review sessions<br/>
        • Apply concepts to real-world scenarios<br/>
        • Stay updated with current developments
        """
        
        story.append(Paragraph(schedule_text, styles['body']))
        story.append(Spacer(1, 0.4 * inch))
        
        story.append(PageBreak())
        return story
    
    def _create_action_plan(self, evaluation_result: dict, styles: dict) -> List:
        """Create personalized action plan"""
        story = []
        
        story.append(Paragraph('<a name="action_plan"/>', styles['body']))
        story.append(Paragraph("🎯 Personalized Action Plan", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        score = evaluation_result.get('score', 0)
        mistakes = evaluation_result.get('mistakes', [])
        
        # Performance-based recommendations
        if score >= 90:
            story.append(Paragraph("🏆 Excellent Performance Action Plan", styles['success']))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("Immediate Actions:", styles['sub_heading']))
            story.append(Paragraph("• Maintain your high level of performance", styles['body']))
            story.append(Paragraph("• Challenge yourself with advanced problems", styles['body']))
            story.append(Paragraph("• Help others learn by explaining concepts", styles['body']))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("Growth Opportunities:", styles['sub_heading']))
            story.append(Paragraph("• Explore advanced topics in the subject", styles['body']))
            story.append(Paragraph("• Consider pursuing certifications", styles['body']))
            story.append(Paragraph("• Mentor other students", styles['body']))
            story.append(Paragraph("• Contribute to study groups or forums", styles['body']))
            
        elif score >= 70:
            story.append(Paragraph("👍 Good Performance Action Plan", styles['info']))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("Immediate Actions:", styles['sub_heading']))
            story.append(Paragraph("• Review mistakes and understand why they occurred", styles['body']))
            story.append(Paragraph("• Focus on weak areas identified in the analysis", styles['body']))
            story.append(Paragraph("• Use the provided study resources", styles['body']))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("Improvement Strategies:", styles['sub_heading']))
            story.append(Paragraph("• Practice with similar questions", styles['body']))
            story.append(Paragraph("• Create study notes for difficult concepts", styles['body']))
            story.append(Paragraph("• Form study groups with peers", styles['body']))
            story.append(Paragraph("• Set specific improvement goals", styles['body']))
            
        else:
            story.append(Paragraph("⚠️ Improvement Action Plan", styles['warning']))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("Immediate Actions:", styles['sub_heading']))
            story.append(Paragraph("• Thoroughly review all incorrect answers", styles['body']))
            story.append(Paragraph("• Focus on fundamental concepts first", styles['body']))
            story.append(Paragraph("• Use basic study resources before advanced ones", styles['body']))
            story.append(Spacer(1, 0.2 * inch))
            
            story.append(Paragraph("Learning Strategies:", styles['sub_heading']))
            story.append(Paragraph("• Break down complex topics into smaller parts", styles['body']))
            story.append(Paragraph("• Use multiple learning methods (videos, reading, practice)", styles['body']))
            story.append(Paragraph("• Seek help from instructors or tutors", styles['body']))
            story.append(Paragraph("• Practice regularly with simpler questions first", styles['body']))
        
        story.append(Spacer(1, 0.4 * inch))
        
        # Specific action items based on mistakes
        if mistakes:
            story.append(Paragraph("🎯 Specific Action Items", styles['sub_heading']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Group mistakes by concept
            concept_mistakes = {}
            for mistake in mistakes:
                concept = mistake.get('concept', 'Unknown')
                if concept not in concept_mistakes:
                    concept_mistakes[concept] = []
                concept_mistakes[concept].append(mistake)
            
            for concept, concept_mistakes_list in concept_mistakes.items():
                story.append(Paragraph(f"<b>For {concept}:</b>", styles['body']))
                story.append(Paragraph(f"• Review {len(concept_mistakes_list)} mistake(s) in this concept", styles['body']))
                story.append(Paragraph("• Complete practice questions on this topic", styles['body']))
                story.append(Paragraph("• Read recommended study materials", styles['body']))
                story.append(Paragraph("• Create summary notes", styles['body']))
                story.append(Spacer(1, 0.1 * inch))
        
        story.append(Spacer(1, 0.4 * inch))
        
        # Progress tracking
        story.append(Paragraph("📊 Progress Tracking", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        tracking_text = """
        <b>Set measurable goals:</b><br/>
        • Target score for next quiz: [Set your goal]<br/>
        • Number of practice questions to complete: [Set target]<br/>
        • Study time per day: [Set schedule]<br/>
        • Review sessions per week: [Set frequency]<br/><br/>
        
        <b>Track your progress:</b><br/>
        • Take regular practice quizzes<br/>
        • Monitor improvement in weak areas<br/>
        • Keep a study journal<br/>
        • Celebrate small victories
        """
        
        story.append(Paragraph(tracking_text, styles['body']))
        story.append(Spacer(1, 0.4 * inch))
        
        story.append(PageBreak())
        return story
    
    def _create_summary(self, evaluation_result: dict, styles: dict) -> List:
        """Create final summary and recommendations"""
        story = []
        
        story.append(Paragraph('<a name="summary"/>', styles['body']))
        story.append(Paragraph("📋 Summary & Final Recommendations", styles['heading']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Performance summary
        score = evaluation_result.get('score', 0)
        total_questions = evaluation_result.get('total_questions', 0)
        correct_answers = evaluation_result.get('correct_answers', 0)
        mistakes = evaluation_result.get('mistakes', [])
        
        story.append(Paragraph("📊 Final Performance Summary", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        accuracy_rate = (correct_answers/total_questions*100) if total_questions > 0 else 0
        summary_text = f"""
        <b>Overall Score:</b> {score:.1f}%<br/>
        <b>Questions Attempted:</b> {total_questions}<br/>
        <b>Correct Answers:</b> {correct_answers}<br/>
        <b>Mistakes:</b> {len(mistakes)}<br/>
        <b>Accuracy Rate:</b> {accuracy_rate:.1f}%<br/>
        <b>Areas for Improvement:</b> {len(set(mistake.get('concept', 'Unknown') for mistake in mistakes))} concepts
        """
        
        story.append(Paragraph(summary_text, styles['info']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Key insights
        story.append(Paragraph("🔍 Key Insights", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        if score >= 90:
            insights = [
                "You have demonstrated excellent understanding of the material",
                "Your knowledge is comprehensive and well-rounded",
                "Consider exploring advanced topics to challenge yourself further",
                "You're ready to help others learn and mentor peers"
            ]
        elif score >= 70:
            insights = [
                "You have a solid foundation in most concepts",
                "Focus on the specific areas where you made mistakes",
                "Regular practice will help you improve further",
                "You're on the right track to mastery"
            ]
        else:
            insights = [
                "Focus on building a strong foundation in the basics",
                "Don't get discouraged - learning is a journey",
                "Use the provided resources to strengthen weak areas",
                "Consider seeking additional help if needed"
            ]
        
        for insight in insights:
            story.append(Paragraph(f"• {insight}", styles['body']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Final recommendations
        story.append(Paragraph("🎯 Final Recommendations", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        recommendations = [
            "Follow the personalized action plan provided in this report",
            "Use the study resources to strengthen weak areas",
            "Practice regularly with similar questions",
            "Track your progress and celebrate improvements",
            "Don't hesitate to seek help when needed",
            "Stay motivated and consistent in your learning journey"
        ]
        
        for i, recommendation in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {recommendation}", styles['body']))
        
        story.append(Spacer(1, 0.4 * inch))
        
        # Motivational message
        story.append(Paragraph("💪 Motivational Message", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        if score >= 90:
            motivational_text = """
            "Excellence is not a skill. It's an attitude." - Ralph Marston<br/><br/>
            You've demonstrated exceptional understanding and dedication to learning. 
            Keep pushing your boundaries and inspiring others with your knowledge!
            """
        elif score >= 70:
            motivational_text = """
            "Success is not final, failure is not fatal: it is the courage to continue that counts." - Winston Churchill<br/><br/>
            You're making great progress! Every mistake is an opportunity to learn and grow stronger.
            Keep up the excellent work!
            """
        else:
            motivational_text = """
            "The only way to do great work is to love what you do." - Steve Jobs<br/><br/>
            Every expert was once a beginner. Your dedication to improvement shows your commitment to learning.
            Stay focused, stay motivated, and you will succeed!
            """
        
        story.append(Paragraph(motivational_text, styles['success']))
        story.append(Spacer(1, 0.4 * inch))
        
        # Next steps
        story.append(Paragraph("🚀 Next Steps", styles['sub_heading']))
        story.append(Spacer(1, 0.2 * inch))
        
        next_steps = [
            "Review this report thoroughly",
            "Implement the action plan",
            "Schedule regular study sessions",
            "Take another quiz in 1-2 weeks to measure progress",
            "Share your learning journey with others",
            "Stay curious and keep learning!"
        ]
        
        for step in next_steps:
            story.append(Paragraph(f"• {step}", styles['body']))
        
        story.append(Spacer(1, 0.6 * inch))
        
        # Footer
        story.append(Paragraph("--- End of Report ---", styles['body']))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['body']))
        story.append(Paragraph("AI-Powered Learning Report System", styles['body']))
        
        return story

    def generate_enhanced_report(self, subject: str, unit: str, evaluation_result: dict, reports_dir: str) -> str:
        """
        Generate enhanced PDF report with improved visuals and structure
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{subject.replace(' ', '_')}_{unit.replace(' ', '_')}_enhanced_report_{timestamp}.pdf"
            report_filepath = os.path.join(reports_dir, report_filename)
            
            logger.info(f"🔍 EnhancedReportGenerator: Creating enhanced report at {report_filepath}")
            
            # Create document
            doc = SimpleDocTemplate(report_filepath, pagesize=A4)
            
            # Generate charts
            charts = self.generate_charts(evaluation_result)
            
            # Create styles
            styles = self._create_styles()
            
            # Build story
            story = []
            
            # Cover page
            story.extend(self._create_cover_page(subject, unit, evaluation_result, styles))
            
            # Table of contents
            story.extend(self._create_table_of_contents(styles))
            
            # Executive summary with charts
            story.extend(self._create_executive_summary(evaluation_result, charts, styles))
            
            # Mistake analysis with review tips
            story.extend(self._create_mistake_analysis(evaluation_result, styles))
            
            # Question review
            story.extend(self._create_question_review(evaluation_result, styles))
            
            # Study resources
            story.extend(self._create_study_resources(evaluation_result, styles))
            
            # Action plan
            story.extend(self._create_action_plan(evaluation_result, styles))
            
            # Summary and recommendations
            story.extend(self._create_summary(evaluation_result, styles))
            
            # Build document
            doc.build(story)
            
            logger.info(f"🔍 EnhancedReportGenerator: Successfully generated enhanced report: {report_filename}")
            return report_filename
            
        except Exception as e:
            logger.error(f"Error generating enhanced report: {e}")
            raise 