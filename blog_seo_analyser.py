#!/usr/bin/env python3
"""
Blog SEO Analyzer for Code A2Z Platform

This script analyzes blog posts (Markdown files) for SEO optimization,
providing recommendations to improve search engine visibility.

Usage:
    python blog_seo_analyzer.py input.md

Features:
    - Analyzes title length and presence
    - Checks keyword density
    - Evaluates content length
    - Suggests meta description
    - Provides SEO score and recommendations
"""

import sys
import os
import re
from collections import Counter
import string

class BlogSEOAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""
        self.title = ""
        self.word_count = 0
        self.keywords = []
        self.analysis_results = {}

    def load_content(self):
        """Load and parse the Markdown file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()

            # Extract title (first # heading)
            title_match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
            if title_match:
                self.title = title_match.group(1).strip()

            # Clean content for analysis (remove markdown syntax)
            self.content = self._clean_markdown(self.content)

        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return False
        return True

    def _clean_markdown(self, text):
        """Remove markdown syntax for text analysis."""
        # Remove headers
        text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove images
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Remove emphasis
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        # Remove lists
        text = re.sub(r'^[\s]*[-\*\+]\s+', '', text, flags=re.MULTILINE)
        return text.strip()

    def analyze_title(self):
        """Analyze title for SEO."""
        if not self.title:
            return {"score": 0, "issues": ["No title found (first # heading)"]}

        length = len(self.title)
        score = 100

        issues = []
        if length < 30:
            score -= 30
            issues.append("Title too short (< 30 characters)")
        elif length > 60:
            score -= 20
            issues.append("Title too long (> 60 characters)")

        # Check for keywords in title
        words = self.title.lower().split()
        if len(words) < 3:
            score -= 10
            issues.append("Title lacks descriptive keywords")

        return {
            "score": max(0, score),
            "length": length,
            "issues": issues,
            "suggestions": ["Include primary keyword in title", "Keep title between 30-60 characters"]
        }

    def analyze_content(self):
        """Analyze content for SEO."""
        words = re.findall(r'\b\w+\b', self.content.lower())
        self.word_count = len(words)

        score = 100
        issues = []

        if self.word_count < 300:
            score -= 40
            issues.append("Content too short (< 300 words)")
        elif self.word_count > 2000:
            score -= 10
            issues.append("Content very long (> 2000 words)")

        # Keyword analysis
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}

        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        word_freq = Counter(filtered_words)

        # Top keywords
        self.keywords = [word for word, count in word_freq.most_common(10) if count > 1]

        # Check keyword density
        if self.keywords:
            primary_keyword = self.keywords[0]
            density = (self.content.lower().count(primary_keyword) / self.word_count) * 100
            if density < 0.5:
                score -= 15
                issues.append("Low keyword density (< 0.5%)")
            elif density > 3:
                score -= 10
                issues.append("High keyword density (> 3% - may be keyword stuffing)")

        return {
            "score": max(0, score),
            "word_count": self.word_count,
            "keywords": self.keywords[:5],  # Top 5
            "issues": issues,
            "suggestions": ["Aim for 300-1500 words", "Use primary keyword naturally", "Include related keywords"]
        }

    def analyze_structure(self):
        """Analyze content structure."""
        score = 100
        issues = []

        # Check for headings
        headings = re.findall(r'^#{2,6}\s+.+', self.content, re.MULTILINE)
        if len(headings) < 2:
            score -= 20
            issues.append("Few or no subheadings (H2-H6)")

        # Check for lists
        lists = len(re.findall(r'^[\s]*[-\*\+]\s+', self.content, re.MULTILINE))
        if lists < 1:
            score -= 10
            issues.append("No bullet lists found")

        # Check for links
        links = len(re.findall(r'\[([^\]]+)\]\([^\)]+\)', self.content))
        if links < 1:
            score -= 5
            issues.append("No internal/external links")

        return {
            "score": max(0, score),
            "headings_count": len(headings),
            "lists_count": lists,
            "links_count": links,
            "issues": issues,
            "suggestions": ["Use H2/H3 headings to structure content", "Include bullet lists for readability", "Add relevant internal/external links"]
        }

    def generate_meta_description(self):
        """Generate a suggested meta description."""
        if not self.title:
            return "No title available for meta description generation"

        # Take first 150-160 characters of content
        clean_content = re.sub(r'\s+', ' ', self.content.strip())
        if len(clean_content) > 150:
            desc = clean_content[:147] + "..."
        else:
            desc = clean_content

        return desc

    def run_analysis(self):
        """Run complete SEO analysis."""
        if not self.load_content():
            return None

        self.analysis_results = {
            "title_analysis": self.analyze_title(),
            "content_analysis": self.analyze_content(),
            "structure_analysis": self.analyze_structure(),
            "meta_description": self.generate_meta_description()
        }

        # Calculate overall score
        scores = [
            self.analysis_results["title_analysis"]["score"],
            self.analysis_results["content_analysis"]["score"],
            self.analysis_results["structure_analysis"]["score"]
        ]
        overall_score = sum(scores) / len(scores)

        self.analysis_results["overall_score"] = round(overall_score, 1)

        return self.analysis_results

    def print_report(self):
        """Print the SEO analysis report."""
        if not self.analysis_results:
            return

        print(f"\n{'='*50}")
        print(f"SEO Analysis Report for: {os.path.basename(self.file_path)}")
        print(f"{'='*50}")

        print(f"\n📊 Overall SEO Score: {self.analysis_results['overall_score']}/100")

        print(f"\n📝 Title Analysis (Score: {self.analysis_results['title_analysis']['score']}/100)")
        if self.title:
            print(f"   Title: {self.title}")
            print(f"   Length: {self.analysis_results['title_analysis']['length']} characters")
        if self.analysis_results['title_analysis']['issues']:
            print("   Issues:")
            for issue in self.analysis_results['title_analysis']['issues']:
                print(f"   - {issue}")
        if self.analysis_results['title_analysis']['suggestions']:
            print("   Suggestions:")
            for sug in self.analysis_results['title_analysis']['suggestions']:
                print(f"   - {sug}")

        print(f"\n📄 Content Analysis (Score: {self.analysis_results['content_analysis']['score']}/100)")
        print(f"   Word Count: {self.analysis_results['content_analysis']['word_count']}")
        if self.keywords:
            print(f"   Top Keywords: {', '.join(self.keywords[:3])}")
        if self.analysis_results['content_analysis']['issues']:
            print("   Issues:")
            for issue in self.analysis_results['content_analysis']['issues']:
                print(f"   - {issue}")
        if self.analysis_results['content_analysis']['suggestions']:
            print("   Suggestions:")
            for sug in self.analysis_results['content_analysis']['suggestions']:
                print(f"   - {sug}")

        print(f"\n🏗️  Structure Analysis (Score: {self.analysis_results['structure_analysis']['score']}/100)")
        print(f"   Headings: {self.analysis_results['structure_analysis']['headings_count']}")
        print(f"   Lists: {self.analysis_results['structure_analysis']['lists_count']}")
        print(f"   Links: {self.analysis_results['structure_analysis']['links_count']}")
        if self.analysis_results['structure_analysis']['issues']:
            print("   Issues:")
            for issue in self.analysis_results['structure_analysis']['issues']:
                print(f"   - {issue}")
        if self.analysis_results['structure_analysis']['suggestions']:
            print("   Suggestions:")
            for sug in self.analysis_results['structure_analysis']['suggestions']:
                print(f"   - {sug}")

        print(f"\n🔍 Suggested Meta Description:")
        print(f"   {self.analysis_results['meta_description']}")

        print(f"\n{'='*50}")

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python blog_seo_analyzer.py <markdown_file>")
        print("Example: python blog_seo_analyzer.py my_blog_post.md")
        sys.exit(1)

    file_path = sys.argv[1]

    analyzer = BlogSEOAnalyzer(file_path)
    results = analyzer.run_analysis()

    if results:
        analyzer.print_report()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
