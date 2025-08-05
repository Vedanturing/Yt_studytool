"""
Enhanced Study Material Generator
Combines yt-dlp for YouTube video scraping, web scraping for articles, and PDF/PPT discovery
"""

import os
import json
import logging
import time
import random
import re
import subprocess
import tempfile
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse, quote_plus
import requests
from bs4 import BeautifulSoup
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import existing AI configuration
try:
    from ai_config import AIConfig
except ImportError:
    class AIConfig:
        @classmethod
        def get_gemini_model(cls):
            return 'gemini-1.5-pro'
        @classmethod
        def is_paid_user(cls):
            return True

logger = logging.getLogger(__name__)

class EnhancedStudyMaterialGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Initialize yt-dlp options
        self.yt_dlp_options = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'max_downloads': 10,
            'ignoreerrors': True,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'live'],
                    'player_skip': ['webpage', 'configs'],
                }
            }
        }
        
        # Educational websites for article scraping
        self.educational_sites = [
            'geeksforgeeks.org',
            'tutorialspoint.com',
            'javatpoint.com',
            'w3schools.com',
            'stackoverflow.com',
            'medium.com',
            'dev.to',
            'freecodecamp.org',
            'khanacademy.org',
            'coursera.org',
            'edx.org',
            'mitopencourseware.org'
        ]
        
        # PDF/PPT search sites
        self.document_sites = [
            'slideshare.net',
            'academia.edu',
            'researchgate.net',
            'scribd.com',
            'docdroid.net',
            'slides.com',
            'prezi.com',
            'canva.com'
        ]
        
        logger.info("✅ Enhanced Study Material Generator initialized")

    def generate_study_materials(self, subject: str, unit: str, topics: List[str]) -> Dict:
        """
        Generate comprehensive study materials using multiple sources
        """
        try:
            logger.info(f"🔍 Generating study materials for {subject} - {unit}")
            
            # Generate search queries
            search_queries = self._generate_search_queries(subject, unit, topics)
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit tasks for parallel execution
                articles_future = executor.submit(self._scrape_articles, search_queries)
                videos_future = executor.submit(self._scrape_youtube_videos, search_queries)
                documents_future = executor.submit(self._scrape_documents, search_queries)
                
                # Collect results
                articles = articles_future.result()
                videos = videos_future.result()
                documents = documents_future.result()
            
            # Combine and format results
            study_materials = {
                "articles": articles[:8],  # Limit to 8 articles
                "videos": videos[:6],      # Limit to 6 videos
                "notes": documents[:6]     # Limit to 6 documents
            }
            
            logger.info(f"✅ Generated {len(articles)} articles, {len(videos)} videos, {len(documents)} documents")
            return study_materials
            
        except Exception as e:
            logger.error(f"❌ Error generating study materials: {e}")
            return self._get_fallback_materials(subject, unit)

    def _generate_search_queries(self, subject: str, unit: str, topics: List[str]) -> List[str]:
        """Generate optimized search queries"""
        queries = []
        
        # Subject + Unit combinations
        queries.extend([
            f"{subject} {unit} tutorial",
            f"{subject} {unit} lecture notes",
            f"{subject} {unit} study guide",
            f"{subject} {unit} examples",
            f"{subject} {unit} practice problems"
        ])
        
        # Topic-specific queries
        for topic in topics[:5]:  # Use first 5 topics
            queries.extend([
                f"{subject} {topic} tutorial",
                f"{topic} examples {subject}",
                f"{topic} study material",
                f"{topic} lecture notes"
            ])
        
        # Educational level specific queries
        queries.extend([
            f"{subject} {unit} for beginners",
            f"{subject} {unit} complete guide",
            f"{subject} {unit} step by step"
        ])
        
        return list(set(queries))  # Remove duplicates

    def _scrape_articles(self, search_queries: List[str]) -> List[Dict]:
        """Scrape educational articles from multiple sources"""
        articles = []
        
        for query in search_queries[:5]:  # Limit to 5 queries
            try:
                logger.info(f"🔍 Scraping articles for: {query}")
                
                # Search on Google for educational sites
                google_results = self._search_google(query, self.educational_sites)
                
                for result in google_results:
                    try:
                        article_data = self._extract_article_data(result['url'], query)
                        if article_data:
                            articles.append(article_data)
                            if len(articles) >= 8:  # Limit total articles
                                break
                    except Exception as e:
                        logger.warning(f"Error extracting article from {result['url']}: {e}")
                        continue
                
                # Add delay to be respectful
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.warning(f"Error scraping articles for query '{query}': {e}")
                continue
        
        return articles

    def _scrape_youtube_videos(self, search_queries: List[str]) -> List[Dict]:
        """Scrape YouTube videos using yt-dlp"""
        videos = []
        
        for query in search_queries[:4]:  # Limit to 4 queries
            try:
                logger.info(f"🎥 Scraping YouTube videos for: {query}")
                
                # Create search URL
                search_url = f"ytsearch10:{query}"
                
                # Use yt-dlp to extract video information
                with yt_dlp.YoutubeDL(self.yt_dlp_options) as ydl:
                    try:
                        # Extract video info
                        video_info = ydl.extract_info(search_url, download=False)
                        
                        if 'entries' in video_info:
                            for entry in video_info['entries']:
                                if entry and len(videos) < 6:  # Limit to 6 videos
                                    video_data = {
                                        "title": entry.get('title', 'Unknown Title'),
                                        "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                        "description": entry.get('description', '')[:200] + '...' if entry.get('description') else f"Video tutorial about {query}",
                                        "source": "YouTube",
                                        "duration": entry.get('duration', 0),
                                        "view_count": entry.get('view_count', 0),
                                        "uploader": entry.get('uploader', 'Unknown'),
                                        "thumbnail": entry.get('thumbnail', '')
                                    }
                                    videos.append(video_data)
                        
                    except Exception as e:
                        logger.warning(f"Error extracting YouTube videos for '{query}': {e}")
                        continue
                
                # Add delay
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.warning(f"Error scraping YouTube videos for query '{query}': {e}")
                continue
        
        return videos

    def _scrape_documents(self, search_queries: List[str]) -> List[Dict]:
        """Scrape PDFs, PPTs, and other educational documents"""
        documents = []
        
        for query in search_queries[:4]:  # Limit to 4 queries
            try:
                logger.info(f"📄 Scraping documents for: {query}")
                
                # Search for documents on Google
                document_queries = [
                    f"{query} filetype:pdf",
                    f"{query} filetype:ppt",
                    f"{query} filetype:pptx",
                    f"{query} slideshare",
                    f"{query} academia.edu"
                ]
                
                for doc_query in document_queries:
                    try:
                        # Search on Google for documents
                        google_results = self._search_google(doc_query, self.document_sites)
                        
                        for result in google_results:
                            try:
                                doc_data = self._extract_document_data(result['url'], query)
                                if doc_data:
                                    documents.append(doc_data)
                                    if len(documents) >= 6:  # Limit total documents
                                        break
                            except Exception as e:
                                logger.warning(f"Error extracting document from {result['url']}: {e}")
                                continue
                        
                        # Add delay
                        time.sleep(random.uniform(1, 2))
                        
                    except Exception as e:
                        logger.warning(f"Error searching documents for '{doc_query}': {e}")
                        continue
                
            except Exception as e:
                logger.warning(f"Error scraping documents for query '{query}': {e}")
                continue
        
        return documents

    def _search_google(self, query: str, allowed_domains: List[str] = None) -> List[Dict]:
        """Search Google for educational content"""
        try:
            # Use a simple Google search approach
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                results = []
                # Look for search result links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Extract actual URL from Google's redirect
                    if href.startswith('/url?q='):
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                    else:
                        actual_url = href
                    
                    # Check if it's a valid URL and from allowed domains
                    if actual_url.startswith('http') and title and len(title) > 10:
                        if allowed_domains:
                            domain = urlparse(actual_url).netloc
                            if any(allowed_domain in domain for allowed_domain in allowed_domains):
                                results.append({
                                    'url': actual_url,
                                    'title': title
                                })
                        else:
                            results.append({
                                'url': actual_url,
                                'title': title
                            })
                
                return results[:5]  # Limit to 5 results
                
        except Exception as e:
            logger.warning(f"Error searching Google for '{query}': {e}")
        
        return []

    def _extract_article_data(self, url: str, query: str) -> Optional[Dict]:
        """Extract article data from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = None
                title_selectors = ['h1', 'title', '.title', '.post-title', '.article-title']
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                if not title:
                    title = f"Article about {query}"
                
                # Extract description
                description = None
                desc_selectors = ['.description', '.summary', '.excerpt', 'meta[name="description"]']
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        if selector == 'meta[name="description"]':
                            description = desc_elem.get('content', '')
                        else:
                            description = desc_elem.get_text(strip=True)
                        break
                
                if not description:
                    # Try to extract first paragraph
                    first_p = soup.find('p')
                    if first_p:
                        description = first_p.get_text(strip=True)[:200] + '...'
                    else:
                        description = f"Educational content about {query}"
                
                # Extract source
                source = urlparse(url).netloc
                
                return {
                    "title": title,
                    "url": url,
                    "description": description,
                    "source": source
                }
                
        except Exception as e:
            logger.warning(f"Error extracting article data from {url}: {e}")
        
        return None

    def _extract_document_data(self, url: str, query: str) -> Optional[Dict]:
        """Extract document data from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = None
                title_selectors = ['h1', 'title', '.title', '.document-title', '.slide-title']
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                if not title:
                    title = f"Document about {query}"
                
                # Extract description
                description = None
                desc_selectors = ['.description', '.summary', '.abstract', 'meta[name="description"]']
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        if selector == 'meta[name="description"]':
                            description = desc_elem.get('content', '')
                        else:
                            description = desc_elem.get_text(strip=True)
                        break
                
                if not description:
                    description = f"Educational document about {query}"
                
                # Determine document type
                doc_type = "Document"
                if '.pdf' in url.lower():
                    doc_type = "PDF"
                elif '.ppt' in url.lower() or '.pptx' in url.lower():
                    doc_type = "Presentation"
                elif 'slideshare' in url.lower():
                    doc_type = "SlideShare"
                elif 'academia.edu' in url.lower():
                    doc_type = "Academic Paper"
                
                # Extract source
                source = urlparse(url).netloc
                
                return {
                    "title": title,
                    "url": url,
                    "description": description,
                    "source": source,
                    "type": doc_type
                }
                
        except Exception as e:
            logger.warning(f"Error extracting document data from {url}: {e}")
        
        return None

    def _get_fallback_materials(self, subject: str, unit: str) -> Dict:
        """Return fallback materials when scraping fails"""
        return {
            "articles": [
                {
                    "title": f"{subject} {unit} - GeeksforGeeks",
                    "url": f"https://www.geeksforgeeks.org/search/?q={quote_plus(f'{subject} {unit}')}",
                    "description": f"Search results for {subject} {unit} on GeeksforGeeks",
                    "source": "GeeksforGeeks"
                },
                {
                    "title": f"{subject} {unit} - TutorialsPoint",
                    "url": f"https://www.tutorialspoint.com/search/search-results?search_string={quote_plus(f'{subject} {unit}')}",
                    "description": f"Search results for {subject} {unit} on TutorialsPoint",
                    "source": "TutorialsPoint"
                }
            ],
            "videos": [
                {
                    "title": f"{subject} {unit} - YouTube Search",
                    "url": f"https://www.youtube.com/results?search_query={quote_plus(f'{subject} {unit} tutorial')}",
                    "description": f"Search results for {subject} {unit} video tutorials on YouTube",
                    "source": "YouTube"
                }
            ],
            "notes": [
                {
                    "title": f"{subject} {unit} - SlideShare Search",
                    "url": f"https://www.slideshare.net/search/slideshow?q={quote_plus(f'{subject} {unit}')}",
                    "description": f"Search results for {subject} {unit} presentations on SlideShare",
                    "source": "SlideShare"
                }
            ]
        }

    def download_youtube_video(self, video_url: str, output_path: str = None) -> Optional[str]:
        """Download a YouTube video using yt-dlp"""
        try:
            if not output_path:
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                output_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            # Configure yt-dlp for download
            download_options = {
                'outtmpl': output_path,
                'format': 'best[height<=720]',  # Limit to 720p
                'quiet': False,
                'no_warnings': False
            }
            
            with yt_dlp.YoutubeDL(download_options) as ydl:
                logger.info(f"📥 Downloading video: {video_url}")
                ydl.download([video_url])
                
                # Return the downloaded file path
                # Note: This is a simplified approach - in practice you'd need to track the actual downloaded file
                return output_path
                
        except Exception as e:
            logger.error(f"❌ Error downloading video {video_url}: {e}")
            return None

    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """Get detailed information about a YouTube video"""
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_options) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    "title": info.get('title', 'Unknown'),
                    "description": info.get('description', ''),
                    "duration": info.get('duration', 0),
                    "view_count": info.get('view_count', 0),
                    "uploader": info.get('uploader', 'Unknown'),
                    "thumbnail": info.get('thumbnail', ''),
                    "upload_date": info.get('upload_date', ''),
                    "tags": info.get('tags', []),
                    "categories": info.get('categories', [])
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting video info for {video_url}: {e}")
            return None 