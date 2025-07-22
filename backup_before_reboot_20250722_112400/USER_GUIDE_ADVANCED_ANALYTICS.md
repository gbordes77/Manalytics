# 🎯 User Guide: Advanced Analytics

> **Practical guide** for using and interpreting advanced metagame analytics

## 📋 Quick Start

### 1. **Running Advanced Analysis**
```bash
# Standard analysis with advanced analytics (automatic)
python run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07

# Results saved to:
# - Analyses/standard_analysis_2025-07-01_2025-07-07/
# - analysis_output/advanced_analysis.json
# - analysis_output/insights_summary.txt
```

### 2. **Viewing Results**
```bash
# Open the HTML report (includes advanced analytics)
open Analyses/standard_analysis_2025-07-01_2025-07-07/rapport_standard_complet.html

# Or check the insights summary
cat analysis_output/insights_summary.txt
```

## 🔬 Understanding Your Results

### **Diversity Metrics** 📊

**What they measure**: How diverse and healthy your metagame is

#### Shannon Diversity Index
- **Range**: 0-4 (higher = more diverse)
- **Interpretation**:
  - `< 1.0`: Very concentrated meta (1-2 dominant archetypes)
  - `1.0-2.0`: Moderately diverse meta (3-7 competitive archetypes)
  - `2.0-3.0`: Highly diverse meta (8-20 competitive archetypes)
  - `> 3.0`: Extremely diverse meta (rare in competitive formats)

#### Simpson Diversity Index
- **Range**: 0-1 (higher = more diverse)
- **Interpretation**:
  - `< 0.5`: Concentrated meta (dominance by few archetypes)
  - `0.5-0.8`: Balanced meta (moderate diversity)
  - `> 0.8`: Diverse meta (many competitive options)

#### Effective Archetypes
- **What it means**: "How many equally popular archetypes would give the same diversity?"
- **Practical use**: Easier to understand than raw Shannon

## 🎨 Visualization Consistency (v0.3.5)

### **What's New in Visual Consistency**

**Perfect Alignment**: All visualizations now show identical archetype ordering and naming.

#### **Hierarchical Ordering**
- **Izzet Prowess**: Always appears first when present
- **Descending Order**: Remaining archetypes ordered by frequency
- **Consistency**: Same order in pie charts, bar charts, and matchup matrix

#### **Unified Naming**
- **Full Names**: "Izzet Prowess" instead of just "Prowess"
- **Color Integration**: "Azorius Omniscience", "Dimir Ramp", "Jeskai Control"
- **Professional**: Industry-standard MTG archetype naming

### **How to Interpret**

#### **Bar Charts**
- **First Position**: Izzet Prowess always leads when present
- **Descending Order**: Next archetypes by percentage
- **Consistent Colors**: Same colors across all chart types

#### **Matchup Matrix**
- **Axes Order**: Both X and Y axes use hierarchical ordering
- **Reading**: Top-left corner always shows Izzet Prowess matchups
- **Navigation**: Logical flow from most to least popular archetypes

#### **Pie Charts**
- **Segments**: Maximum 12 segments for optimal readability
- **Ordering**: Clockwise from most to least popular
- **No "Others"**: Only specific archetypes shown

### **Benefits for Analysis**
- **Easier Comparison**: Same order makes cross-chart analysis intuitive
- **Professional Consistency**: Industry-standard presentation
- **Reduced Confusion**: No more wondering why charts show different orders
- **Example**: Shannon=1.95 → ~7 effective archetypes

**🎯 Actionable Insights**:
```
Shannon = 1.2, Effective = 3.3 archetypes
→ "Meta is moderately concentrated around 3-4 main archetypes"
→ Good for competitive play, but watch for potential stagnation

Shannon = 2.8, Effective = 16.4 archetypes
→ "Highly diverse meta with many viable options"
→ Great for brewing, but harder to predict tournament outcomes
```

---

### **Temporal Trends** 📈

**What they show**: How archetype popularity changes over time

#### Trend Categories
1. **Rising** 📈: Positive trend with good fit (R² > 0.3)
   - *Action*: Watch for continued growth, consider playing or countering
2. **Declining** 📉: Negative trend with good fit (R² > 0.3)
   - *Action*: Avoid unless you expect a comeback
3. **Volatile** 🎪: Inconsistent trends (R² < 0.3, high variance)
   - *Action*: Unpredictable, follow recent tournaments closely
4. **Stable** ⚖️: Consistent share (R² < 0.3, low variance)
   - *Action*: Reliable meta staple, safe choice

#### Reading the Data
```json
{
  "Azorius Control": {
    "trend_category": "Rising",
    "slope": 0.023,           // +2.3% per week
    "r_squared": 0.67,        // Strong trend reliability
    "mean_share": 0.15        // 15% average meta share
  }
}
```

**🎯 Actionable Insights**:
```
Rising: Domain Zoo (+12.3%), Jeskai Control (+8.7%)
→ "These archetypes are gaining popularity - expect to face them more"
→ Consider sideboard cards that help against these matchups

Declining: Rakdos Midrange (-15.2%), Mono-Red Aggro (-9.1%)
→ "These archetypes are losing favor - less common in upcoming events"
→ May be under-represented = potential surprise factor
```

---

### **Archetype Clustering** 🎯

**What it shows**: Groups archetypes by similar performance characteristics

#### Typical Cluster Patterns
1. **Cluster 0 - Meta Leaders**: High share + High winrate
   - *Archetypes*: Tier 1 decks, tournament favorites
   - *Action*: Master these or prepare to beat them
2. **Cluster 1 - Niche Performers**: Low share + High winrate
   - *Archetypes*: Underplayed but strong decks
   - *Action*: Potential sleeper picks for tournaments
3. **Cluster 2 - Popular Underperformers**: High share + Low winrate
   - *Archetypes*: Overhyped or declining decks
   - *Action*: Good to play against, avoid playing

#### Reading Cluster Results
```json
{
  "archetype_clusters": {
    "Rakdos Midrange": 0,     // Meta Leader
    "Dimir Control": 1,       // Niche Performer
    "Mono-Red Aggro": 2       // Popular Underperformer
  }
}
```

**🎯 Actionable Insights**:
```
Meta Leaders (Cluster 0): Rakdos Midrange, Azorius Control
→ "These are the decks to beat - high share AND high winrate"
→ Tournament preparation should focus on these matchups

Niche Performers (Cluster 1): Dimir Control, Jeskai Combo
→ "Hidden gems - strong winrate but low popularity"
→ Good candidates for competitive advantage
```

---

### **Correlation Analysis** 🔗

**What it shows**: Statistical relationships between metrics

#### Correlation Strength
- **Strong**: |r| > 0.7 (very reliable relationship)
- **Moderate**: 0.3 < |r| ≤ 0.7 (noticeable trend)
- **Weak**: |r| ≤ 0.3 (little to no relationship)

#### Common Correlations
1. **Winrate vs Meta Share**
   - Positive: "Good decks become popular"
   - Negative: "Popular decks get targeted/countered"
2. **Wins vs Losses**
   - Usually negative: "More wins = fewer losses"
3. **Matches Played vs Meta Share**
   - Positive: "Popular decks play more matches"

**🎯 Actionable Insights**:
```
Strong Correlation: Winrate vs Meta Share (r=0.73)
→ "In this meta, successful decks quickly gain popularity"
→ Follow tournament results closely for emerging archetypes

Weak Correlation: Wins vs Meta Share (r=0.12)
→ "Popular decks aren't necessarily the most successful"
→ Don't just copy the most-played decks
```

---

## 🎪 Strategic Applications

### **For Tournament Preparation**

#### 1. **Archetype Selection**
```python
# Look for niche performers
if archetype in cluster_1_archetypes:
    print(f"{archetype} might be undervalued")

# Avoid popular underperformers
if archetype in cluster_2_archetypes:
    print(f"{archetype} might be overplayed")
```

#### 2. **Sideboard Planning**
```python
# Target rising archetypes
rising_archetypes = [arch for arch, data in temporal_analysis.items()
                    if data['trend_category'] == 'Rising']
print(f"Prepare sideboard for: {rising_archetypes}")
```

#### 3. **Meta Timing**
```python
# High diversity = unpredictable
if shannon_diversity > 2.5:
    print("High diversity - favor adaptable decks")

# Low diversity = predictable
if shannon_diversity < 1.5:
    print("Concentrated meta - favor targeted hate")
```

### **For Content Creation**

#### 1. **Deck Guides**
```python
# Focus on trending archetypes
trending = rising_archetypes + volatile_archetypes
print(f"Hot topics for content: {trending}")
```

#### 2. **Meta Analysis**
```python
# Explain cluster patterns
for cluster, profile in cluster_profiles.items():
    print(f"Cluster {cluster}: {profile['characteristics']}")
```

### **For Competitive Analysis**

#### 1. **Opponent Prediction**
```python
# Most likely opponents based on meta share
top_archetypes = sorted(meta_shares.items(), key=lambda x: x[1], reverse=True)
print(f"Expect to face: {top_archetypes[:5]}")
```

#### 2. **Advantage Identification**
```python
# Underplayed but strong archetypes
advantages = [arch for arch in niche_performers
             if arch not in popular_archetypes]
print(f"Competitive advantages: {advantages}")
```

---

## 🚀 Advanced Usage Tips

### **Combining Metrics**
```python
# Find the "sweet spot" archetypes
sweet_spot = []
for archetype, data in temporal_analysis.items():
    if (data['trend_category'] == 'Rising' and
        archetype in niche_performers and
        diversity_metrics['evenness'] > 0.7):
        sweet_spot.append(archetype)

print(f"Optimal archetype choices: {sweet_spot}")
```

### **Historical Comparison**
```python
# Track diversity over time
previous_shannon = 1.85
current_shannon = 2.12

if current_shannon > previous_shannon:
    print("Meta is becoming more diverse")
else:
    print("Meta is consolidating")
```

### **Statistical Validation**
```python
# Check if correlations are statistically significant
significant_correlations = [
    corr for corr in correlations
    if corr['p_value'] < 0.05
]
print(f"Statistically significant patterns: {significant_correlations}")
```

---

## 📋 Common Scenarios

### **Scenario 1: New Format Launch**
```
Shannon < 1.5, Many Rising archetypes
→ "Format is still settling, expect rapid changes"
→ Strategy: Play adaptable decks, watch for breakout archetypes
```

### **Scenario 2: Mature Format**
```
Shannon 1.8-2.2, Mostly Stable archetypes
→ "Format is established with clear tier structure"
→ Strategy: Master tier 1 decks or find niche counters
```

### **Scenario 3: Ban/Unban Event**
```
Many Volatile archetypes, Changing clusters
→ "Format is adapting to rule changes"
→ Strategy: Watch for new trends, test extensively
```

### **Scenario 4: Tournament Season**
```
High correlation between winrate and meta share
→ "Results-driven meta, performance matters"
→ Strategy: Focus on proven performers, avoid experimental builds
```

---

## 🎯 Quick Reference

### **Health Check**
- Shannon > 2.0 = Healthy diversity
- Simpson > 0.8 = Good balance
- Effective archetypes > 6 = Many viable options

### **Trend Signals**
- Rising + Niche Performer = Hidden gem
- Declining + Popular = Avoid
- Volatile + Meta Leader = Watch closely

### **Correlation Patterns**
- Strong positive winrate/share = Meritocratic meta
- Weak winrate/share = Popularity-driven meta
- Strong negative = Counter-adaptation happening

### **Action Items**
1. **Check diversity**: Is the meta healthy?
2. **Identify trends**: What's rising/falling?
3. **Find clusters**: Any undervalued archetypes?
4. **Examine correlations**: What drives success?
5. **Plan strategy**: Based on combined insights

---

## 🔗 Related Resources

- [API Reference](API_REFERENCE_ADVANCED_ANALYTICS.md): Technical documentation
- [Orchestrator Integration](ORCHESTRATOR_INTEGRATION.md): Pipeline details
- [Implementation Summary](IMPLEMENTATION_SUMMARY_v0.3.4.md): Feature overview

---

*For questions or support, check the GitHub repository or contact the development team.*
