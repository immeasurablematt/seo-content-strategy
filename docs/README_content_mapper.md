# Content Calendar & Topical Authority Mapper for io.net

A comprehensive SEO and content strategy tool that uses DataForSEO API for keyword research and Claude AI for content strategy insights. This tool creates topical clusters, assesses domain authority, identifies content gaps, and generates a 90-day content calendar.

## Features

- **Keyword Research**: Comprehensive keyword discovery using DataForSEO API
- **Topical Clustering**: AI-powered clustering of keywords into content themes
- **Authority Assessment**: Analysis of current domain rankings and authority scores
- **Content Gap Analysis**: Identification of high-opportunity content gaps
- **Content Hub Strategy**: Pillar and cluster content structure recommendations
- **90-Day Content Calendar**: AI-generated strategic content calendar
- **Competitive Analysis**: Compare against competitors and identify gaps
- **Performance Tracking**: Monitor content performance over time
- **Internal Linking**: Suggestions for internal linking opportunities

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. API Credentials

Copy the environment template and add your API credentials:

```bash
cp env_template.txt .env
```

Edit `.env` with your credentials:

```env
# DataForSEO API Credentials
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password

# Anthropic API Key for Claude
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Get API Keys

- **DataForSEO**: Sign up at [app.dataforseo.com](https://app.dataforseo.com/)
- **Anthropic**: Get your API key from [console.anthropic.com](https://console.anthropic.com/)

## Usage

### Quick Start

Run the complete analysis with key insights:

```bash
python quick_start.py
```

This will:
- Build a comprehensive keyword dataset
- Create topical clusters
- Assess current authority
- Identify content gaps
- Generate content hubs
- Create a 90-day content calendar
- Generate Excel and markdown reports

### Main Analysis

Run the full analysis pipeline:

```bash
python content_authority_mapper.py
```

### Advanced Features

Run advanced competitive analysis and content tracking:

```bash
python advanced_analysis.py
```

## Output Files

The tool generates several output files:

1. **Excel Report** (`ionet_content_strategy_YYYYMMDD_HHMMSS.xlsx`):
   - Keywords sheet with clusters and authority scores
   - Cluster summary with metrics
   - Content calendar with 90-day plan
   - Content hubs with priority scores

2. **Executive Summary** (`ionet_executive_summary_YYYYMMDD_HHMMSS.md`):
   - AI-generated strategic summary
   - Current state assessment
   - Key opportunities
   - Strategic recommendations

3. **JSON Data** (`ionet_data_YYYYMMDD_HHMMSS.json`):
   - Raw data for programmatic use
   - Keywords, hubs, and calendar data

4. **Competitor Reports** (from advanced analysis):
   - Competitive gap analysis
   - Content performance tracking
   - Internal linking suggestions

## Key Components

### ContentAuthorityMapper Class

Main class that handles:
- DataForSEO API integration
- Keyword research and clustering
- Authority assessment
- Content strategy generation

### AdvancedAnalyzer Class

Extended features for:
- Competitive analysis
- Content performance tracking
- Internal linking suggestions
- Content velocity analysis

## Example Usage

```python
from content_authority_mapper import ContentAuthorityMapper

# Initialize mapper
mapper = ContentAuthorityMapper()

# Run full analysis
df, hubs, calendar = mapper.run_full_analysis()

# Access specific insights
top_gaps = df[df['content_strategy'] == 'High Priority Gap'].nlargest(10, 'opportunity_score')
print(top_gaps[['keyword', 'search_volume', 'competition', 'opportunity_score']])
```

## Content Strategy Framework

The tool implements a comprehensive content strategy framework:

1. **Seed Keywords**: 15 core keywords related to decentralized GPU computing
2. **Keyword Expansion**: Related keywords and search volume data
3. **Topical Clustering**: AI-powered grouping into content themes
4. **Authority Assessment**: Current ranking analysis
5. **Gap Identification**: High-opportunity content gaps
6. **Hub Structure**: Pillar and supporting content organization
7. **Content Calendar**: 90-day strategic content plan

## Business Goals

The content strategy focuses on:
- **Developer Adoption**: Technical content for developers
- **Network Growth**: Content to attract GPU providers
- **SEO Authority**: Building topical authority in key areas
- **Thought Leadership**: Positioning io.net as industry leader

## Rate Limiting

The tool includes built-in rate limiting for API calls:
- 1-second delay between DataForSEO requests
- Efficient batching of API calls
- Error handling for API failures

## Troubleshooting

### Common Issues

1. **API Credentials**: Ensure your `.env` file has correct credentials
2. **Rate Limiting**: The tool handles rate limiting automatically
3. **Memory Usage**: Large datasets may require significant memory
4. **API Quotas**: Monitor your DataForSEO API usage

### Error Handling

The tool includes comprehensive error handling:
- API request failures are logged and skipped
- Missing data is handled gracefully
- Progress indicators show current status

## Contributing

To extend the tool:

1. Add new seed keywords in `get_seed_keywords()`
2. Extend clustering logic in `create_topical_clusters()`
3. Add new analysis methods in `AdvancedAnalyzer`
4. Customize content calendar generation in `generate_calendar_with_claude()`

## License

This tool is designed for io.net's content strategy needs. Adapt as needed for your organization.

