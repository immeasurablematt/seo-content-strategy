# SEO Content Strategy Tool

A powerful AI-powered SEO content strategy tool that generates comprehensive content briefs, analyzes keyword competition, and creates content calendars using DataForSEO API and Claude AI.

## 📖 About

The SEO Content Strategy Tool is designed to solve the common problem of creating data-driven, competitive content that actually ranks. Instead of guessing what content to create, this tool analyzes real search results, measures actual competitor content, and provides AI-powered strategic recommendations.

### 🎯 What Makes This Different

**Real Data, Not Estimates**
- Fetches actual SERP results from Google
- Measures real word counts from competitor pages
- Uses live domain authority metrics
- Analyzes actual content gaps and opportunities

**AI-Powered Strategy**
- Claude AI analyzes competitors to recommend target audiences
- Identifies underserved content opportunities
- Generates comprehensive content briefs with specific recommendations
- Provides strategic insights based on competitive analysis

**Comprehensive Analysis**
- Keyword research with search volume and competition data
- Domain authority comparison against competitors
- Content length analysis based on top-ranking pages
- Internal linking recommendations
- 90-day content calendar generation

### 🚀 Perfect For

- **Content Marketers** who want data-driven content strategies
- **SEO Professionals** who need comprehensive competitive analysis
- **Content Teams** looking to create better, more strategic content
- **Businesses** wanting to outrank competitors with superior content
- **Agencies** that need to deliver detailed content briefs to clients

### 💡 How It Works

1. **Input**: You provide a target keyword
2. **Research**: Tool fetches real SERP data and competitor metrics
3. **Analysis**: AI analyzes competitors to identify gaps and opportunities
4. **Strategy**: Generates comprehensive content brief with specific recommendations
5. **Output**: You get a detailed brief ready for content creation

## 🚀 Quick Start

### 1. Setup (First Time Only)
```bash
python setup.py
```

### 2. Add Your API Keys
Edit the `.env` file and add your API credentials:
```bash
# Get these from:
# - Anthropic: https://console.anthropic.com/
# - DataForSEO: https://app.dataforseo.com/
ANTHROPIC_API_KEY=your_key_here
DATAFORSEO_LOGIN=your_login_here
DATAFORSEO_PASSWORD=your_password_here
```

### 3. Generate Your First Brief
```bash
python scripts/generate_brief.py
```

## 📁 Project Structure

```
seo-content-strategy/
├── 📄 setup.py                   # First-time setup
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # This file
│
├── 📁 scripts/                   # Executable scripts
│   ├── generate_brief.py         # Generate individual SEO briefs
│   ├── run_analysis.py           # Content authority analysis
│   ├── batch_enhanced_briefs.py  # Batch brief generation
│   ├── batch_live_sitemap_briefs.py # Batch with live sitemap
│   ├── run_brief_with_progress.py # Progress tracking
│   └── start_web_app.py          # Web interface
│
├── 📁 src/                       # Core functionality modules
│   ├── simple_seo_brief.py       # Brief generation engine
│   ├── content_authority_mapper.py # Authority analysis
│   ├── keyword_competitor_analyzer.py # Competitor analysis
│   ├── advanced_analysis.py      # Extended features
│   ├── streamlit_app.py          # Web interface
│   ├── enhanced_internal_links.py # Enhanced internal linking
│   ├── live_sitemap_internal_links.py # Live sitemap integration
│   ├── updated_simple_seo_brief.py # Updated brief generator
│   └── improve_brief_generator.py # Enhanced brief generator
│
├── 📁 reports/                   # Generated analysis reports
│   ├── ionet_content_strategy_*.xlsx # Excel reports
│   ├── ionet_data_*.json         # JSON data exports
│   └── ionet_executive_summary_*.md # Executive summaries
│
├── 📁 generated_briefs/          # Generated SEO briefs
│   ├── *.md                      # Markdown briefs
│   └── *.docx                    # Word document briefs
│
├── 📁 converters/                # File format conversion tools
│   ├── convert_brief_to_docx.py  # DOCX conversion utilities
│   ├── convert_to_docx.py        # Quick DOCX converter
│   └── enhanced_docx_converter.py # Enhanced formatting
│
├── 📁 tests/                     # Test scripts
│   └── test_live_sitemap.py      # Live sitemap tests
│
├── 📁 config/                    # Configuration
│   ├── settings.py               # App settings
│   └── env_template.txt          # Environment template
│
├── 📁 data/                      # Data files
│   ├── *.csv                     # Keyword data, internal links
│   └── *.log                     # Log files
│
├── 📁 docs/                      # Documentation
│   ├── USAGE_GUIDE.md            # Detailed usage guide
│   ├── README_content_mapper.md  # Content mapper docs
│   └── *.md                      # Additional documentation
│
├── 📁 backups/                   # Backup files
└── 📁 output/                    # Generated reports (auto-created)
```

## 🎯 What This Tool Does

### 1. **SEO Content Briefs** (`generate_brief.py`)
- Analyzes top 10 search results for your keyword
- Compares domain authority of competitors
- Measures actual content length of top competitors
- Auto-recommends target audience and content goals
- Generates comprehensive content briefs with:
  - Keyword strategy and placement
  - Content structure (H2/H3 outline)
  - Competition analysis
  - Internal linking recommendations
  - Word count targets based on competitors

### 2. **Content Authority Analysis** (`run_analysis.py`)
- Keyword research and clustering
- Authority assessment for your domain
- Content gap identification
- 90-day content calendar generation
- Excel and markdown reports

### 3. **Web Interface** (`start_web_app.py`)
- User-friendly web interface
- Real-time brief generation
- Interactive competition analysis
- Download briefs as markdown files

## 🛠️ Usage Examples

### Generate a Single Brief
```bash
python generate_brief.py
```
The script will prompt you for:
- Primary keyword (e.g., "gpu cluster for machine learning")
- Target audience (optional - auto-detected)
- Content goal (optional - auto-detected)
- Your domain (optional - defaults to io.net)

### Run Full Content Analysis
```bash
python run_analysis.py
```
Generates comprehensive content strategy with:
- Keyword clusters and authority scores
- Content calendar
- Excel reports
- Strategic recommendations

### Use Web Interface
```bash
python start_web_app.py
```
Opens a web interface at http://localhost:8501

## 📊 Output Files

### Content Briefs
- `{keyword}-brief.md` - Comprehensive SEO brief
- Includes competition analysis, content structure, and recommendations

### Content Analysis
- `ionet_content_strategy_YYYYMMDD_HHMMSS.xlsx` - Excel report
- `ionet_executive_summary_YYYYMMDD_HHMMSS.md` - AI insights
- `ionet_data_YYYYMMDD_HHMMSS.json` - Raw data

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password

# Optional
DEFAULT_DOMAIN=io.net
DEFAULT_LOCATION_CODE=2840  # US
DEFAULT_LANGUAGE_CODE=en
```

### Customization
Edit `config/settings.py` to modify:
- Seed keywords
- Default settings
- Competition thresholds
- Output preferences

## 📚 Documentation

- **Detailed Guide**: `docs/USAGE_GUIDE.md`
- **Content Mapper**: `docs/README_content_mapper.md`
- **API Documentation**: Check individual script files

## 🆘 Troubleshooting

### Common Issues

1. **"No .env file found"**
   ```bash
   cp config/env_template.txt .env
   # Then edit .env with your API keys
   ```

2. **"Module not found" errors**
   ```bash
   python setup.py  # Reinstall dependencies
   ```

3. **API errors**
   - Check your API keys in `.env`
   - Verify API quotas and limits
   - Check internet connection

4. **Streamlit not found**
   ```bash
   pip install streamlit
   ```

### Getting Help
1. Run `python setup.py` to verify installation
2. Check the console output for specific error messages
3. Ensure all API credentials are valid and have sufficient quota

## 🎯 Key Features

- **AI-Powered Analysis**: Uses Claude AI for strategic insights
- **Real Competitor Data**: Fetches actual SERP results and domain metrics
- **Content Length Analysis**: Measures real word counts from competitor pages
- **Auto-Audience Detection**: Analyzes competitors to recommend target audience
- **Comprehensive Briefs**: 10+ sections covering all SEO aspects
- **Multiple Output Formats**: Markdown, Excel, JSON
- **Web Interface**: User-friendly Streamlit app
- **Batch Processing**: Analyze multiple keywords at once

## 📈 What Makes This Different

1. **Real Data**: Uses actual SERP results, not estimates
2. **Competitor Analysis**: Measures real content lengths and domain authority
3. **AI Strategy**: Claude AI provides strategic recommendations
4. **Comprehensive**: Covers keyword research, competition, content strategy, and more
5. **Actionable**: Provides specific, implementable recommendations

## 🔄 Workflow

1. **Setup** → Run `python setup.py` once
2. **Configure** → Add API keys to `.env`
3. **Generate** → Run `python generate_brief.py`
4. **Review** → Check generated brief
5. **Create** → Use brief to write content
6. **Track** → Monitor performance and iterate

---

**Need help?** Check the documentation in the `docs/` folder or run the setup script to verify your installation.
