# Content Authority Mapper - Usage Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set Up API Credentials**
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual API credentials
   ```

3. **Test Setup**
   ```bash
   python3 test_setup.py
   ```

4. **Run Analysis**
   ```bash
   python3 quick_start.py
   ```

## Available Scripts

### 1. `quick_start.py` - Main Analysis
Runs the complete content authority analysis:
- Keyword research and clustering
- Authority assessment
- Content gap identification
- 90-day content calendar generation
- Excel and markdown reports

### 2. `content_authority_mapper.py` - Core Engine
The main class and functions for content strategy analysis.

### 3. `advanced_analysis.py` - Extended Features
Additional analysis tools:
- Competitive gap analysis
- Content performance tracking
- Internal linking suggestions
- Content velocity analysis

### 4. `test_setup.py` - Setup Verification
Tests that all dependencies are installed and configured correctly.

## Output Files

After running the analysis, you'll get:

1. **Excel Report** (`ionet_content_strategy_YYYYMMDD_HHMMSS.xlsx`)
   - Keywords with clusters and authority scores
   - Cluster summaries
   - Content calendar
   - Content hubs

2. **Executive Summary** (`ionet_executive_summary_YYYYMMDD_HHMMSS.md`)
   - AI-generated strategic insights
   - Current state assessment
   - Key opportunities
   - Recommendations

3. **JSON Data** (`ionet_data_YYYYMMDD_HHMMSS.json`)
   - Raw data for programmatic use

## API Requirements

- **DataForSEO Account**: For keyword research and SERP analysis
- **Anthropic API Key**: For Claude AI content strategy insights

## Customization

### Adding New Seed Keywords
Edit the `get_seed_keywords()` method in `content_authority_mapper.py`:

```python
def get_seed_keywords(self) -> List[str]:
    return [
        "your new keyword",
        "another keyword",
        # ... existing keywords
    ]
```

### Modifying Content Strategy
Customize the content calendar generation in `generate_calendar_with_claude()` method.

### Adding Competitors
Update the competitor list in `advanced_analysis.py`:

```python
competitors = ['competitor1.com', 'competitor2.com', 'competitor3.com']
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Run `pip3 install -r requirements.txt`
2. **API Errors**: Check your `.env` file has correct credentials
3. **Memory Issues**: The tool processes large datasets - ensure sufficient RAM
4. **Rate Limiting**: Built-in delays handle API rate limits

### Getting Help

1. Run `python3 test_setup.py` to verify setup
2. Check the console output for specific error messages
3. Ensure all API credentials are valid and have sufficient quota

## Example Workflow

```python
from content_authority_mapper import ContentAuthorityMapper

# Initialize
mapper = ContentAuthorityMapper()

# Run full analysis
df, hubs, calendar = mapper.run_full_analysis()

# Access insights
top_gaps = df[df['content_strategy'] == 'High Priority Gap']
print(f"Found {len(top_gaps)} high-priority content gaps")

# Check content hubs
for name, data in hubs.items():
    print(f"{name}: {data['priority_score']:.1f} priority score")
```

## Next Steps

1. Review the generated Excel report for detailed insights
2. Read the executive summary for strategic recommendations
3. Use the content calendar to plan your content production
4. Run competitive analysis to identify additional opportunities
5. Track content performance over time using the advanced features

