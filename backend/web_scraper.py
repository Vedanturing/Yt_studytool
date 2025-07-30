"""
Web Scraper for Study Materials
Searches for real study materials, videos, and resources based on topics and concepts
Uses Gemini AI as fallback when web scraping fails
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional
import os
import json
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

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

class StudyMaterialScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize Gemini for fallback
        self.gemini_model = None
        if GEMINI_AVAILABLE and AIConfig.GEMINI_API_KEY:
            try:
                genai.configure(api_key=AIConfig.GEMINI_API_KEY)
                model_name = AIConfig.get_gemini_model()
                self.gemini_model = genai.GenerativeModel(model_name)
                quota_info = AIConfig.get_quota_info()
                logger.info(f"✅ Gemini model initialized for study material generation with {model_name} ({quota_info})")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini for study materials: {e}")
        
    def search_study_materials(self, subject: str, unit: str, topics: List[str]) -> Dict:
        """
        Search for study materials based on subject, unit, and topics
        Returns structured data with articles, videos, and notes
        """
        try:
            logger.info(f"Searching study materials for {subject} - {unit}")
            
            # Create search queries
            search_queries = self._generate_search_queries(subject, unit, topics)
            
            articles = []
            videos = []
            notes = []
            
            # Try web scraping first
            for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limiting
                logger.info(f"Searching for: {query}")
                
                # Search for articles
                articles.extend(self._search_articles(query))
                
                # Search for videos
                videos.extend(self._search_videos(query))
                
                # Search for notes/PDFs
                notes.extend(self._search_notes(query))
                
                # Add delay to be respectful
                time.sleep(random.uniform(1, 3))
            
            # Check if we got any results from web scraping
            if articles or videos or notes:
                logger.info(f"✅ Web scraping successful: {len(articles)} articles, {len(videos)} videos, {len(notes)} notes")
                return {
                    "articles": articles[:6],  # Limit to 6 articles
                    "videos": videos[:4],      # Limit to 4 videos
                    "notes": notes[:4]         # Limit to 4 notes
                }
            else:
                logger.warning("⚠️ No web scraping results, trying Gemini AI fallback")
                # Try Gemini AI as the first fallback
                gemini_materials = self._get_gemini_fallback_materials(subject, unit, topics)
                if gemini_materials.get("articles") or gemini_materials.get("videos") or gemini_materials.get("notes"):
                    logger.info("✅ Successfully generated study materials with Gemini AI fallback.")
                    return gemini_materials
                else:
                    logger.warning("⚠️ Gemini AI fallback also failed, using static fallback materials")
                    return self._get_fallback_materials(subject, unit)
            
        except Exception as e:
            logger.error(f"Error searching study materials: {e}")
            logger.info("🔄 Attempting Gemini AI fallback due to web scraping error")
            
            # If web scraping fails completely, try Gemini AI
            gemini_materials = self._get_gemini_fallback_materials(subject, unit, topics)
            if gemini_materials.get("articles") or gemini_materials.get("videos") or gemini_materials.get("notes"):
                logger.info("✅ Successfully generated study materials with Gemini AI fallback.")
                return gemini_materials
            else:
                logger.warning("⚠️ Gemini AI fallback also failed due to error, using static fallback materials")
                return self._get_fallback_materials(subject, unit)
    
    def _generate_search_queries(self, subject: str, unit: str, topics: List[str]) -> List[str]:
        """Generate search queries for web scraping"""
        queries = []
        
        # Subject + Unit queries
        queries.append(f"{subject} {unit} study guide")
        queries.append(f"{subject} {unit} tutorial")
        queries.append(f"{subject} {unit} lecture notes")
        
        # Topic-specific queries
        for topic in topics[:3]:  # Use first 3 topics
            queries.append(f"{subject} {topic} tutorial")
            queries.append(f"{subject} {topic} examples")
            queries.append(f"{topic} study material")
        
        return queries
    
    def _search_articles(self, query: str) -> List[Dict]:
        """Search for articles and tutorials"""
        articles = []
        
        try:
            # Search on educational websites
            sites = [
                f"https://www.geeksforgeeks.org/search/?q={query.replace(' ', '+')}",
                f"https://www.tutorialspoint.com/search/search-results?search_string={query.replace(' ', '+')}",
                f"https://www.javatpoint.com/search?q={query.replace(' ', '+')}",
                f"https://www.w3schools.com/search/search.php?q={query.replace(' ', '+')}"
            ]
            
            for site in sites:
                try:
                    response = self.session.get(site, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_site(soup, site, query))
                except Exception as e:
                    logger.warning(f"Error scraping {site}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
        
        return articles
    
    def _search_videos(self, query: str) -> List[Dict]:
        """Search for educational videos"""
        videos = []
        
        try:
            # Search on educational video platforms
            video_sites = [
                f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
                f"https://www.khanacademy.org/search?page_search_query={query.replace(' ', '+')}",
                f"https://www.coursera.org/search?query={query.replace(' ', '+')}"
            ]
            
            for site in video_sites:
                try:
                    response = self.session.get(site, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        videos.extend(self._extract_videos_from_site(soup, site, query))
                except Exception as e:
                    logger.warning(f"Error scraping videos from {site}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
        
        return videos
    
    def _search_notes(self, query: str) -> List[Dict]:
        """Search for notes, PDFs, and study materials"""
        notes = []
        
        try:
            # Search for PDFs and study materials
            pdf_sites = [
                f"https://www.slideshare.net/search/slideshow?searchfrom=header&q={query.replace(' ', '+')}",
                f"https://www.academia.edu/search?q={query.replace(' ', '+')}",
                f"https://www.researchgate.net/search/publication?q={query.replace(' ', '+')}"
            ]
            
            for site in pdf_sites:
                try:
                    response = self.session.get(site, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        notes.extend(self._extract_notes_from_site(soup, site, query))
                except Exception as e:
                    logger.warning(f"Error scraping notes from {site}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
        
        return notes
    
    def _extract_articles_from_site(self, soup: BeautifulSoup, base_url: str, query: str) -> List[Dict]:
        """Extract articles from a website"""
        articles = []
        
        try:
            # Look for article links
            links = soup.find_all('a', href=True)
            
            for link in links[:10]:  # Limit to 10 links
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title and len(title) > 10:
                    # Check if it's a relevant article
                    if any(keyword in title.lower() for keyword in query.lower().split()):
                        full_url = urljoin(base_url, href)
                        
                        articles.append({
                            "title": title,
                            "url": full_url,
                            "description": f"Article about {query}",
                            "source": urlparse(base_url).netloc
                        })
                        
                        if len(articles) >= 3:  # Limit to 3 articles per site
                            break
                            
        except Exception as e:
            logger.error(f"Error extracting articles: {e}")
        
        return articles
    
    def _extract_videos_from_site(self, soup: BeautifulSoup, base_url: str, query: str) -> List[Dict]:
        """Extract videos from a website"""
        videos = []
        
        try:
            # Look for video links
            links = soup.find_all('a', href=True)
            
            for link in links[:10]:  # Limit to 10 links
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title and len(title) > 10:
                    # Check if it's a video link
                    if any(keyword in title.lower() for keyword in ['video', 'tutorial', 'lecture', 'course']):
                        full_url = urljoin(base_url, href)
                        
                        videos.append({
                            "title": title,
                            "url": full_url,
                            "description": f"Video tutorial about {query}",
                            "source": urlparse(base_url).netloc
                        })
                        
                        if len(videos) >= 2:  # Limit to 2 videos per site
                            break
                            
        except Exception as e:
            logger.error(f"Error extracting videos: {e}")
        
        return videos
    
    def _extract_notes_from_site(self, soup: BeautifulSoup, base_url: str, query: str) -> List[Dict]:
        """Extract notes and study materials from a website"""
        notes = []
        
        try:
            # Look for document links
            links = soup.find_all('a', href=True)
            
            for link in links[:10]:  # Limit to 10 links
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title and len(title) > 10:
                    # Check if it's a document link
                    if any(ext in href.lower() for ext in ['.pdf', '.ppt', '.doc', '.docx']) or \
                       any(keyword in title.lower() for keyword in ['notes', 'slides', 'presentation', 'pdf']):
                        full_url = urljoin(base_url, href)
                        
                        notes.append({
                            "title": title,
                            "url": full_url,
                            "description": f"Study material about {query}",
                            "source": urlparse(base_url).netloc
                        })
                        
                        if len(notes) >= 2:  # Limit to 2 notes per site
                            break
                            
        except Exception as e:
            logger.error(f"Error extracting notes: {e}")
        
        return notes
    
    def _get_gemini_fallback_materials(self, subject: str, unit: str, topics: List[str]) -> Dict:
        """Use Gemini AI to generate study materials when web scraping fails"""
        try:
            if not self.gemini_model:
                logger.warning("⚠️ Gemini not available, using static fallback materials")
                return self._get_fallback_materials(subject, unit)
            
            logger.info(f"🤖 Using Gemini AI to generate study materials for {subject} - {unit}")
            
            # Create context for Gemini
            topics_text = ", ".join(topics)
            prompt = f"""
            Subject: {subject}
            Unit: {unit}
            Topics: {topics_text}
            
            Generate study materials for this unit. Provide 3 articles, 2 videos, and 2 notes with realistic titles, descriptions, and URLs to educational websites.
            
            Format the response as a JSON object with this exact structure:
            {{
                "articles": [
                    {{
                        "title": "Article Title",
                        "url": "https://real-educational-website.com/article",
                        "description": "Brief description of the article content",
                        "source": "Website Name"
                    }}
                ],
                "videos": [
                    {{
                        "title": "Video Title",
                        "url": "https://youtube.com/watch?v=...",
                        "description": "Brief description of the video content",
                        "source": "YouTube"
                    }}
                ],
                "notes": [
                    {{
                        "title": "Notes Title",
                        "url": "https://slideshare.net/...",
                        "description": "Brief description of the notes content",
                        "source": "SlideShare"
                    }}
                ]
            }}
            
            Make sure the URLs are realistic and point to actual educational websites like GeeksforGeeks, TutorialsPoint, YouTube, SlideShare, etc.
            Focus on the specific topics provided and make the content relevant to the subject and unit.
            
            Return only the JSON object, no additional text.
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text.strip()
            
            # Try to extract JSON from response
            if content.startswith('{') and content.endswith('}'):
                materials = json.loads(content)
                logger.info(f"✅ Generated {len(materials.get('articles', []))} articles, {len(materials.get('videos', []))} videos, {len(materials.get('notes', []))} notes with Gemini")
                return materials
            else:
                # Try to find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx + 1]
                    materials = json.loads(json_str)
                    logger.info(f"✅ Generated {len(materials.get('articles', []))} articles, {len(materials.get('videos', []))} videos, {len(materials.get('notes', []))} notes with Gemini")
                    return materials
                    
        except Exception as e:
            logger.error(f"Error with Gemini fallback generation: {e}")
        
        # If Gemini fails, use static fallback
        logger.warning("⚠️ Gemini fallback for study materials failed, using static fallback materials")
        return self._get_fallback_materials(subject, unit)
    
    def _get_fallback_materials(self, subject: str, unit: str) -> Dict:
        """Return comprehensive fallback materials when web scraping fails"""
        
        # Create subject-specific materials based on the subject
        if "operating system" in subject.lower():
            return self._get_os_fallback_materials(unit)
        elif "software engineering" in subject.lower():
            return self._get_se_fallback_materials(unit)
        elif "data analytics" in subject.lower():
            return self._get_da_fallback_materials(unit)
        else:
            return self._get_generic_fallback_materials(subject, unit)
    
    def _get_os_fallback_materials(self, unit: str) -> Dict:
        """Get Operating System specific fallback materials"""
        materials = {
            "articles": [
                {
                    "title": f"Operating System Tutorials - GeeksforGeeks",
                    "url": "https://www.geeksforgeeks.org/operating-systems-tutorials/",
                    "description": f"General tutorials and articles on Operating Systems concepts from GeeksforGeeks.",
                    "source": "GeeksforGeeks"
                },
                {
                    "title": f"Operating System Learning - TutorialsPoint",
                    "url": "https://www.tutorialspoint.com/operating_system/index.htm",
                    "description": f"Main page for Operating System tutorials on TutorialsPoint.",
                    "source": "TutorialsPoint"
                },
                {
                    "title": f"Operating System Concepts - Javatpoint",
                    "url": "https://www.javatpoint.com/operating-system-tutorial",
                    "description": f"Comprehensive guide to Operating System concepts on Javatpoint.",
                    "source": "Javatpoint"
                }
            ],
            "videos": [
                {
                    "title": f"Operating System Full Course - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query=operating+system+full+course",
                    "description": f"Search results for a complete video course on Operating Systems.",
                    "source": "YouTube"
                },
                {
                    "title": f"OS Concepts NPTEL Lectures - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query=nptel+operating+system+lectures",
                    "description": f"Search results for NPTEL video lectures on Operating Systems.",
                    "source": "YouTube (NPTEL)"
                }
            ],
            "notes": [
                {
                    "title": f"Operating System Lecture Notes - SlideShare Search",
                    "url": f"https://www.slideshare.net/search/slideshow?q=operating+system+lecture+notes",
                    "description": f"Search results for lecture notes and presentations on Operating Systems.",
                    "source": "SlideShare"
                },
                {
                    "title": f"Operating System Study Material - Academia.edu Search",
                    "url": f"https://www.academia.edu/search?q=operating+system+study+material",
                    "description": f"Search results for academic papers and study materials on Operating Systems.",
                    "source": "Academia.edu"
                }
            ]
        }
        
        # Add unit-specific materials if they are more reliable and general
        # Using more general search queries for unit-specific content
        if "process" in unit.lower():
            materials["articles"].append({
                "title": "Process Management - GeeksforGeeks Search",
                "url": "https://www.geeksforgeeks.org/search/?q=process+management+operating+system",
                "description": "Search results for process management concepts in OS on GeeksforGeeks.",
                "source": "GeeksforGeeks"
            })
        elif "memory" in unit.lower():
            materials["articles"].append({
                "title": "Memory Management - GeeksforGeeks Search",
                "url": "https://www.geeksforgeeks.org/search/?q=memory+management+operating+system",
                "description": "Search results for memory management concepts in OS on GeeksforGeeks.",
                "source": "GeeksforGeeks"
            })
        elif "file" in unit.lower():
            materials["articles"].append({
                "title": "File Systems - GeeksforGeeks Search",
                "url": "https://www.geeksforgeeks.org/search/?q=file+systems+operating+system",
                "description": "Search results for file system concepts in OS on GeeksforGeeks.",
                "source": "GeeksforGeeks"
            })
        
        return materials
    
    def _get_se_fallback_materials(self, unit: str) -> Dict:
        """Get Software Engineering specific fallback materials"""
        return {
            "articles": [
                {
                    "title": f"Software Engineering Tutorials - GeeksforGeeks",
                    "url": "https://www.geeksforgeeks.org/software-engineering-tutorials/",
                    "description": f"General tutorials and articles on Software Engineering from GeeksforGeeks.",
                    "source": "GeeksforGeeks"
                },
                {
                    "title": f"Software Engineering Learning - TutorialsPoint",
                    "url": "https://www.tutorialspoint.com/software_engineering/index.htm",
                    "description": f"Main page for Software Engineering tutorials on TutorialsPoint.",
                    "source": "TutorialsPoint"
                },
                {
                    "title": f"Software Engineering Concepts - Javatpoint",
                    "url": "https://www.javatpoint.com/software-engineering-tutorial",
                    "description": f"Comprehensive guide to Software Engineering concepts on Javatpoint.",
                    "source": "Javatpoint"
                }
            ],
            "videos": [
                {
                    "title": f"Software Engineering Full Course - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query=software+engineering+full+course",
                    "description": f"Search results for a complete video course on Software Engineering.",
                    "source": "YouTube"
                },
                {
                    "title": f"SDLC Tutorial - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query=software+development+life+cycle+tutorial",
                    "description": f"Search results for video tutorials on Software Development Life Cycle.",
                    "source": "YouTube"
                }
            ],
            "notes": [
                {
                    "title": f"Software Engineering Lecture Notes - SlideShare Search",
                    "url": f"https://www.slideshare.net/search/slideshow?q=software+engineering+lecture+notes",
                    "description": f"Search results for lecture notes and presentations on Software Engineering.",
                    "source": "SlideShare"
                },
                {
                    "title": f"Software Engineering Study Material - Academia.edu Search",
                    "url": f"https://www.academia.edu/search?q=software+engineering+study+material",
                    "description": f"Search results for academic papers and study materials on Software Engineering.",
                    "source": "Academia.edu"
                }
            ]
        }
    
    def _get_da_fallback_materials(self, unit: str) -> Dict:
        """Get Data Analytics specific fallback materials"""
        return {
            "articles": [
                {
                    "title": f"Data Analytics Tutorials - GeeksforGeeks",
                    "url": "https://www.geeksforgeeks.org/data-analytics-tutorial/",
                    "description": f"General tutorials and articles on Data Analytics from GeeksforGeeks.",
                    "source": "GeeksforGeeks"
                },
                {
                    "title": f"Data Analytics Learning - TutorialsPoint",
                    "url": "https://www.tutorialspoint.com/data_analytics/index.htm",
                    "description": f"Main page for Data Analytics tutorials on TutorialsPoint.",
                    "source": "TutorialsPoint"
                },
                {
                    "title": f"Data Analytics Concepts - Javatpoint",
                    "url": "https://www.javatpoint.com/data-analytics-tutorial",
                    "description": f"Comprehensive guide to Data Analytics concepts on Javatpoint.",
                    "source": "Javatpoint"
                }
            ],
            "videos": [
                {
                    "title": f"Data Analytics Full Course - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query=data+analytics+full+course",
                    "description": f"Search results for a complete video course on Data Analytics.",
                    "source": "YouTube"
                },
                {
                    "title": f"Data Visualization Tutorial - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query=data+visualization+tutorial",
                    "description": f"Search results for video tutorials on Data Visualization techniques.",
                    "source": "YouTube"
                }
            ],
            "notes": [
                {
                    "title": f"Data Analytics Lecture Notes - SlideShare Search",
                    "url": f"https://www.slideshare.net/search/slideshow?q=data+analytics+lecture+notes",
                    "description": f"Search results for lecture notes and presentations on Data Analytics.",
                    "source": "SlideShare"
                },
                {
                    "title": f"Data Analytics Study Material - Academia.edu Search",
                    "url": f"https://www.academia.edu/search?q=data+analytics+study+material",
                    "description": f"Search results for academic papers and study materials on Data Analytics.",
                    "source": "Academia.edu"
                }
            ]
        }
    
    def _get_generic_fallback_materials(self, subject: str, unit: str) -> Dict:
        """Get generic fallback materials for any subject"""
        # Using general search queries for maximum reliability
        return {
            "articles": [
                {
                    "title": f"Learn {subject} - GeeksforGeeks Search",
                    "url": f"https://www.geeksforgeeks.org/search/?q={subject.replace(' ', '+')}",
                    "description": f"Search results for {subject} on GeeksforGeeks.",
                    "source": "GeeksforGeeks"
                },
                {
                    "title": f"{subject} Tutorials - TutorialsPoint Search",
                    "url": f"https://www.tutorialspoint.com/search/search-results?search_string={subject.replace(' ', '+')}",
                    "description": f"Search results for {subject} tutorials on TutorialsPoint.",
                    "source": "TutorialsPoint"
                }
            ],
            "videos": [
                {
                    "title": f"{subject} Course - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query={subject.replace(' ', '+')}+course",
                    "description": f"Search results for {subject} video courses on YouTube.",
                    "source": "YouTube"
                }
            ],
            "notes": [
                {
                    "title": f"{subject} Lecture Notes - SlideShare Search",
                    "url": f"https://www.slideshare.net/search/slideshow?q={subject.replace(' ', '+')}+lecture+notes",
                    "description": f"Search results for {subject} lecture notes on SlideShare.",
                    "source": "SlideShare"
                }
            ]
        } 