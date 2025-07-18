import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Import PDF parsing libraries
try:
    import PyPDF2
    PDF_PARSING_AVAILABLE = True
except ImportError:
    PDF_PARSING_AVAILABLE = False
    print("Warning: PyPDF2 not available for syllabus parsing.")

logger = logging.getLogger(__name__)

# Path to diploma syllabus folder
SYLLABUS_DIR = Path("diploma_syllabus")

def parse_pdf_syllabus(file_path: Path) -> Dict[str, List[str]]:
    """Parse a PDF syllabus file and extract units and topics"""
    if not PDF_PARSING_AVAILABLE:
        logger.warning("PDF parsing not available, returning empty units")
        return {}
    
    try:
        units = {}
        current_unit = None
        current_topics = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Look for unit patterns
                    unit_match = re.search(r'Unit\s*(\d+)[:\-]?\s*(.+)', line, re.IGNORECASE)
                    if unit_match:
                        # Save previous unit if exists
                        if current_unit:
                            units[current_unit] = current_topics
                        
                        # Start new unit
                        unit_num = unit_match.group(1)
                        unit_title = unit_match.group(2).strip()
                        current_unit = f"Unit {unit_num}"
                        current_topics = []
                        
                        # Add unit title as first topic if it's descriptive
                        if unit_title and len(unit_title) > 3:
                            current_topics.append(unit_title)
                    
                    # Look for topic patterns (numbered items)
                    topic_match = re.search(r'^\s*(\d+\.?)\s*(.+)', line)
                    if topic_match and current_unit:
                        topic = topic_match.group(2).strip()
                        if topic and len(topic) > 3:
                            current_topics.append(topic)
                    
                    # Look for subtopic patterns (letters or dashes)
                    subtopic_match = re.search(r'^\s*([a-z]\.?|-)\s*(.+)', line, re.IGNORECASE)
                    if subtopic_match and current_unit:
                        subtopic = subtopic_match.group(2).strip()
                        if subtopic and len(subtopic) > 3:
                            current_topics.append(subtopic)
        
        # Add the last unit
        if current_unit:
            units[current_unit] = current_topics
        
        return units
        
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return {}

def get_detailed_subjects() -> Dict[str, Dict]:
    """Get detailed subject information from PDF files"""
    subjects = {
        "315319-OPERATING SYSTEM": {
            "name": "Operating System",
            "pdf_file": "315319-OPERATING SYSTEM.pdf",
            "description": "Comprehensive study of operating system concepts, process management, memory management, and system architecture.",
            "units": {}
        },
        "315321-ADVANCE COMPUTER NETWORK": {
            "name": "Advanced Computer Network",
            "pdf_file": "315321-ADVANCE COMPUTER NETWORK.pdf", 
            "description": "Advanced networking concepts including OSI model, TCP/IP protocols, routing algorithms, and network security.",
            "units": {}
        },
        "315323-SOFTWARE ENGINEERING": {
            "name": "Software Engineering",
            "pdf_file": "315323-SOFTWARE ENGINEERING.pdf",
            "description": "Software development methodologies, system analysis, design patterns, and project management principles.",
            "units": {}
        }
    }
    
    # Parse PDF files if available
    if SYLLABUS_DIR.exists():
        for subject_code, subject_data in subjects.items():
            pdf_file = SYLLABUS_DIR / subject_data["pdf_file"]
            if pdf_file.exists():
                logger.info(f"Parsing syllabus for {subject_code}")
                units = parse_pdf_syllabus(pdf_file)
                if units:
                    subject_data["units"] = units
                else:
                    # Fallback to default units if parsing fails
                    subject_data["units"] = get_default_units(subject_code)
            else:
                logger.warning(f"PDF file not found: {pdf_file}")
                subject_data["units"] = get_default_units(subject_code)
    else:
        logger.warning(f"Syllabus directory not found: {SYLLABUS_DIR}")
        # Use default units for all subjects
        for subject_code in subjects:
            subjects[subject_code]["units"] = get_default_units(subject_code)
    
    return subjects

def get_default_units(subject_code: str) -> Dict[str, List[str]]:
    """Get default units for subjects when PDF parsing is not available"""
    default_units = {
        "315319-OPERATING SYSTEM": {
            "Unit 1": [
                "Introduction to Operating Systems",
                "OS Functions and Services", 
                "Types of Operating Systems",
                "System Calls and Interrupts",
                "Operating System Architecture"
            ],
            "Unit 2": [
                "Process Management",
                "Process States and Lifecycle",
                "Process Scheduling Algorithms",
                "Interprocess Communication",
                "Thread Management"
            ],
            "Unit 3": [
                "Memory Management",
                "Virtual Memory Concepts",
                "Page Replacement Algorithms",
                "Memory Allocation Strategies",
                "Memory Protection and Security"
            ],
            "Unit 4": [
                "File Systems",
                "File Organization Methods",
                "Directory Structure and Management",
                "File Operations and Access Control",
                "File System Implementation"
            ],
            "Unit 5": [
                "Device Management",
                "I/O Systems and Controllers",
                "Device Drivers and Interfaces",
                "Disk Scheduling Algorithms",
                "Storage Management"
            ]
        },
        "315321-ADVANCE COMPUTER NETWORK": {
            "Unit 1": [
                "Network Fundamentals",
                "OSI Reference Model",
                "TCP/IP Protocol Suite",
                "Network Topologies and Architecture",
                "Network Standards and Organizations"
            ],
            "Unit 2": [
                "Data Link Layer",
                "Error Detection and Correction",
                "Flow Control Mechanisms",
                "Medium Access Control Protocols",
                "Data Link Layer Protocols"
            ],
            "Unit 3": [
                "Network Layer",
                "Routing Algorithms and Protocols",
                "IP Addressing and Subnetting",
                "Network Layer Protocols",
                "Quality of Service (QoS)"
            ],
            "Unit 4": [
                "Transport Layer",
                "TCP Protocol and Features",
                "UDP Protocol and Applications",
                "Congestion Control Mechanisms",
                "Transport Layer Security"
            ],
            "Unit 5": [
                "Application Layer",
                "HTTP and Web Protocols",
                "DNS and Name Resolution",
                "Email Protocols and Services",
                "Network Security and Cryptography"
            ]
        },
        "315323-SOFTWARE ENGINEERING": {
            "Unit 1": [
                "Software Engineering Introduction",
                "Software Process Models",
                "Software Development Life Cycle",
                "Requirements Engineering",
                "Software Project Management"
            ],
            "Unit 2": [
                "System Analysis",
                "Data Flow Diagrams (DFD)",
                "Entity Relationship Diagrams (ERD)",
                "System Design Principles",
                "System Architecture Design"
            ],
            "Unit 3": [
                "Object-Oriented Analysis",
                "UML Diagrams and Notation",
                "Class Diagrams and Relationships",
                "Use Case Diagrams and Scenarios",
                "Object-Oriented Design Patterns"
            ],
            "Unit 4": [
                "Software Testing",
                "Testing Strategies and Levels",
                "Unit Testing and Integration Testing",
                "System Testing and Acceptance Testing",
                "Test Case Design and Execution"
            ],
            "Unit 5": [
                "Software Maintenance",
                "Software Quality Assurance",
                "Software Metrics and Measurement",
                "Project Management and Planning",
                "Software Configuration Management"
            ]
        }
    }
    
    return default_units.get(subject_code, {})

def get_subject_summary(subject_code: str) -> Dict[str, str]:
    """Get a summary of what students will learn in each subject"""
    summaries = {
        "315319-OPERATING SYSTEM": {
            "overview": "Master the fundamentals of operating systems including process management, memory allocation, and system architecture.",
            "skills": "Process scheduling, memory management, file systems, device drivers",
            "career": "System Administrator, OS Developer, Embedded Systems Engineer",
            "difficulty": "Intermediate to Advanced"
        },
        "315321-ADVANCE COMPUTER NETWORK": {
            "overview": "Learn advanced networking concepts, protocols, and network security principles for modern computer networks.",
            "skills": "Network design, protocol analysis, routing, network security",
            "career": "Network Engineer, Network Administrator, Security Specialist",
            "difficulty": "Advanced"
        },
        "315323-SOFTWARE ENGINEERING": {
            "overview": "Develop software engineering skills including system analysis, design patterns, and project management methodologies.",
            "skills": "System analysis, UML modeling, software testing, project management",
            "career": "Software Engineer, System Analyst, Project Manager",
            "difficulty": "Intermediate"
        }
    }
    
    return summaries.get(subject_code, {
        "overview": "Comprehensive study of computer science concepts and applications.",
        "skills": "Problem solving, analytical thinking, technical implementation",
        "career": "Software Developer, IT Professional, System Analyst",
        "difficulty": "Intermediate"
    })

if __name__ == "__main__":
    # Test the syllabus parser
    subjects = get_detailed_subjects()
    for code, data in subjects.items():
        print(f"\n{code}: {data['name']}")
        print(f"Description: {data['description']}")
        print("Units:")
        for unit, topics in data['units'].items():
            print(f"  {unit}: {len(topics)} topics")
            for topic in topics[:3]:  # Show first 3 topics
                print(f"    - {topic}")
            if len(topics) > 3:
                print(f"    ... and {len(topics) - 3} more topics") 