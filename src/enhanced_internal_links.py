#!/usr/bin/env python3
"""
Enhanced Internal Linking Analysis for io.net Content Strategy

This script enhances the internal linking functionality by:
1. Analyzing topic clusters for better internal linking
2. Providing strategic anchor text recommendations
3. Identifying link equity distribution opportunities
4. Creating internal linking maps for content clusters
"""

import os
import json
import pandas as pd
from typing import List, Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class EnhancedInternalLinker:
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.internal_pages = self.load_internal_pages()
        
    def load_internal_pages(self) -> List[Dict]:
        """Load internal pages from CSV"""
        pages = []
        csv_path = "data/Internal-Links-Oct-10- 2025.csv"
        
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                pages.append({
                    'category': row.get('Category', ''),
                    'title': row.get('Page Title', ''),
                    'url': row.get('URL', ''),
                    'description': row.get('Description', ''),
                    'keywords': row.get('Keywords', '')
                })
            print(f"✅ Loaded {len(pages)} internal pages")
            return pages
        except Exception as e:
            print(f"❌ Error loading internal pages: {e}")
            return []
    
    def analyze_cluster_links(self, primary_keyword: str, cluster_name: str, target_audience: str) -> Dict:
        """Analyze internal links for a specific topic cluster"""
        print(f"\n🔗 Analyzing internal links for '{primary_keyword}' in {cluster_name}...")
        
        # Categorize pages by relevance to cluster
        cluster_relevant_pages = self.categorize_pages_by_cluster(cluster_name)
        
        # Get strategic recommendations
        recommendations = self.get_strategic_link_recommendations(
            primary_keyword, cluster_name, target_audience, cluster_relevant_pages
        )
        
        return recommendations
    
    def categorize_pages_by_cluster(self, cluster_name: str) -> Dict[str, List[Dict]]:
        """Categorize internal pages by their relevance to topic clusters"""
        
        # Define cluster mappings
        cluster_mappings = {
            "CLUSTER 1: GPU FOR AI FUNDAMENTALS": {
                "high_relevance": ["Blog", "Docs"],
                "keywords": ["GPU", "AI", "training", "infrastructure", "compute"],
                "exclude": ["Legal", "Support", "Community"]
            },
            "CLUSTER 2: GPU FOR AI TRAINING & DEVELOPMENT": {
                "high_relevance": ["Blog", "Docs", "App"],
                "keywords": ["training", "development", "ML", "models", "deployment"],
                "exclude": ["Legal", "Support"]
            },
            "CLUSTER 3: GPU CLOUD PROVIDERS & SERVICES": {
                "high_relevance": ["Product", "Blog", "App", "Explorer"],
                "keywords": ["cloud", "providers", "services", "platform", "deployment"],
                "exclude": ["Legal", "Support"]
            },
            "CLUSTER 4: GPU SERVER INFRASTRUCTURE": {
                "high_relevance": ["Product", "Blog", "Docs", "App"],
                "keywords": ["infrastructure", "servers", "deployment", "clusters"],
                "exclude": ["Legal", "Support", "Community"]
            },
            "CLUSTER 5: AI CLOUD COMPUTING ECOSYSTEM": {
                "high_relevance": ["Blog", "Product", "App"],
                "keywords": ["cloud", "AI", "computing", "ecosystem", "platform"],
                "exclude": ["Legal", "Support"]
            },
            "CLUSTER 6: AI CLOUD SERVICES & PLATFORMS": {
                "high_relevance": ["Product", "Blog", "App", "Docs"],
                "keywords": ["services", "platforms", "AI", "cloud", "intelligence"],
                "exclude": ["Legal", "Support"]
            },
            "CLUSTER 7: BEST AI/CLOUD TOOLS & APIS": {
                "high_relevance": ["Product", "Blog", "Docs", "App"],
                "keywords": ["tools", "APIs", "intelligence", "models", "integration"],
                "exclude": ["Legal", "Support"]
            }
        }
        
        cluster_config = cluster_mappings.get(cluster_name, {
            "high_relevance": ["Blog", "Docs", "Product"],
            "keywords": [],
            "exclude": ["Legal", "Support"]
        })
        
        categorized = {
            "high_relevance": [],
            "medium_relevance": [],
            "supporting": []
        }
        
        for page in self.internal_pages:
            category = page.get('category', '')
            keywords = page.get('keywords', '').lower()
            
            # Skip excluded categories
            if category in cluster_config["exclude"]:
                continue
            
            # Check for high relevance
            if category in cluster_config["high_relevance"]:
                # Check keyword relevance
                keyword_match = any(keyword in keywords for keyword in cluster_config["keywords"])
                if keyword_match:
                    categorized["high_relevance"].append(page)
                else:
                    categorized["medium_relevance"].append(page)
            elif category not in ["Legal", "Support", "Community"]:
                categorized["supporting"].append(page)
        
        return categorized
    
    def get_strategic_link_recommendations(self, primary_keyword: str, cluster_name: str, 
                                         target_audience: str, categorized_pages: Dict) -> Dict:
        """Get strategic internal link recommendations using Claude AI"""
        
        # Prepare data for Claude
        high_relevance_str = "\n".join([
            f"- {p['title']} ({p['url']}) - {p['description'][:100]}..."
            for p in categorized_pages["high_relevance"][:10]
        ])
        
        medium_relevance_str = "\n".join([
            f"- {p['title']} ({p['url']}) - {p['description'][:100]}..."
            for p in categorized_pages["medium_relevance"][:10]
        ])
        
        prompt = f"""You are an SEO strategist creating internal linking recommendations for io.net content.

PRIMARY KEYWORD: {primary_keyword}
CLUSTER: {cluster_name}
TARGET AUDIENCE: {target_audience}

HIGH RELEVANCE PAGES:
{high_relevance_str}

MEDIUM RELEVANCE PAGES:
{medium_relevance_str}

Create strategic internal linking recommendations that:

1. **Pillar Content Links** (2-3 links): Future comprehensive guides that should receive link equity
2. **Supporting Content Links** (2-3 links): Related articles that add value and context
3. **Product/Service Links** (1-2 links): Relevant io.net products or services
4. **Resource Links** (1-2 links): Documentation, tools, or helpful resources

For each link, provide:
- Strategic purpose (pillar support, user journey, authority building)
- Placement recommendation (introduction, body, conclusion)
- Anchor text suggestion (natural, keyword-rich, contextual)

Return as JSON:
{{
  "pillar_content": [
    {{
      "title": "Page Title",
      "url": "https://io.net/...",
      "anchor_text": "suggested anchor text",
      "placement": "introduction|body|conclusion",
      "strategic_purpose": "explanation of why this link matters"
    }}
  ],
  "supporting_content": [...],
  "product_service": [...],
  "resources": [...],
  "link_equity_strategy": "Explanation of how these links distribute authority",
  "user_journey_optimization": "How these links guide users through the funnel"
}}"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(response_text)
            return recommendations
            
        except Exception as e:
            print(f"⚠️ Error getting strategic recommendations: {e}")
            return {"error": str(e)}
    
    def generate_internal_link_map(self, keywords: List[str]) -> Dict:
        """Generate an internal linking map for multiple keywords"""
        print(f"\n🗺️ Generating internal linking map for {len(keywords)} keywords...")
        
        link_map = {}
        
        for keyword in keywords:
            # Determine cluster based on keyword
            cluster = self.determine_cluster_for_keyword(keyword)
            
            # Get recommendations for this keyword
            recommendations = self.analyze_cluster_links(
                keyword, cluster, "Technical decision-makers and developers"
            )
            
            link_map[keyword] = {
                "cluster": cluster,
                "recommendations": recommendations
            }
        
        return link_map
    
    def determine_cluster_for_keyword(self, keyword: str) -> str:
        """Determine which cluster a keyword belongs to"""
        keyword_lower = keyword.lower()
        
        if any(term in keyword_lower for term in ["gpu", "ai", "fundamentals", "vs cpu"]):
            return "CLUSTER 1: GPU FOR AI FUNDAMENTALS"
        elif any(term in keyword_lower for term in ["training", "development", "ml"]):
            return "CLUSTER 2: GPU FOR AI TRAINING & DEVELOPMENT"
        elif any(term in keyword_lower for term in ["providers", "cloud", "services"]):
            return "CLUSTER 3: GPU CLOUD PROVIDERS & SERVICES"
        elif any(term in keyword_lower for term in ["servers", "infrastructure"]):
            return "CLUSTER 4: GPU SERVER INFRASTRUCTURE"
        elif any(term in keyword_lower for term in ["cloud computing", "ecosystem"]):
            return "CLUSTER 5: AI CLOUD COMPUTING ECOSYSTEM"
        elif any(term in keyword_lower for term in ["cloud services", "platforms"]):
            return "CLUSTER 6: AI CLOUD SERVICES & PLATFORMS"
        elif any(term in keyword_lower for term in ["apis", "tools"]):
            return "CLUSTER 7: BEST AI/CLOUD TOOLS & APIS"
        else:
            return "CLUSTER 1: GPU FOR AI FUNDAMENTALS"  # Default
    
    def save_link_map(self, link_map: Dict, filename: str = None):
        """Save internal linking map to JSON file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'internal_link_map_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(link_map, f, indent=2)
        
        print(f"✅ Internal linking map saved to: {filename}")
        return filename

def main():
    """Main function to demonstrate enhanced internal linking"""
    linker = EnhancedInternalLinker()
    
    # Example: Generate internal link map for priority keywords
    priority_keywords = [
        "gpu vs cpu for ai",
        "cloud computing and ai", 
        "best ai apis",
        "gpu cloud providers",
        "ai cloud services"
    ]
    
    # Generate link map
    link_map = linker.generate_internal_link_map(priority_keywords)
    
    # Save results
    filename = linker.save_link_map(link_map)
    
    print(f"\n🎉 Enhanced internal linking analysis complete!")
    print(f"📄 Results saved to: {filename}")
    
    return link_map

if __name__ == "__main__":
    main()
