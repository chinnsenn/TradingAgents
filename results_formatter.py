import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class HTMLTemplateBuilder:
    """Builder for creating consistent HTML templates"""
    
    @staticmethod
    def create_report_template(content: str, title: str, custom_classes: str = "") -> str:
        """Create a standardized report template"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
        <div class='report-container {custom_classes}'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {timestamp}</div>
            </div>
            <div class='report-content'>
                {content}
            </div>
        </div>
        """
    
    @staticmethod
    def create_placeholder(message: str) -> str:
        """Create a placeholder div"""
        return f"<div class='report-placeholder'>{message}</div>"

class ResultsFormatter:
    """Handles formatting of analysis results for web display"""
    
    def __init__(self):
        self.report_titles = {
            "market_report": "📈 Market Analysis",
            "sentiment_report": "📱 Social Sentiment Analysis",
            "news_report": "📰 News Analysis",
            "fundamentals_report": "💼 Fundamentals Analysis",
            "investment_plan": "🎯 Research Team Decision",
            "trader_investment_plan": "💰 Trading Plan",
            "final_trade_decision": "⚖️ Final Trading Decision",
        }
        
        self.team_colors = {
            "Analyst Team": "#007bff",
            "Research Team": "#28a745",
            "Trading Team": "#ffc107",
            "Risk Management": "#dc3545",
            "Portfolio Management": "#6f42c1",
        }
    
    def format_market_report(self, report: str) -> str:
        """Format market analysis report for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("Market analysis pending...")
        
        html_content = self._markdown_to_html(report)
        enhanced_content = self._enhance_tables(html_content)
        return HTMLTemplateBuilder.create_report_template(enhanced_content, "📈 Market Analysis")
    
    def format_sentiment_report(self, report: str) -> str:
        """Format social sentiment report for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("Social sentiment analysis pending...")
        
        html_content = self._markdown_to_html(report)
        return HTMLTemplateBuilder.create_report_template(html_content, "📱 Social Sentiment Analysis")
    
    def format_news_report(self, report: str) -> str:
        """Format news analysis report for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("News analysis pending...")
        
        html_content = self._markdown_to_html(report)
        formatted_content = self._format_news_items(html_content)
        return HTMLTemplateBuilder.create_report_template(formatted_content, "📰 News Analysis")
    
    def format_fundamentals_report(self, report: str) -> str:
        """Format fundamentals analysis report for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("Fundamentals analysis pending...")
        
        html_content = self._markdown_to_html(report)
        highlighted_content = self._highlight_financial_metrics(html_content)
        return HTMLTemplateBuilder.create_report_template(highlighted_content, "💼 Fundamentals Analysis")
    
    def format_research_decision(self, report: str) -> str:
        """Format research team decision for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("Research team decision pending...")
        
        html_content = self._markdown_to_html(report)
        formatted_content = self._format_bull_bear_sections(html_content)
        return HTMLTemplateBuilder.create_report_template(formatted_content, "🎯 Research Team Decision")
    
    def format_trading_plan(self, report: str) -> str:
        """Format trading plan for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("Trading plan pending...")
        
        html_content = self._markdown_to_html(report)
        formatted_content = self._format_action_items(html_content)
        return HTMLTemplateBuilder.create_report_template(formatted_content, "💰 Trading Plan")
    
    def format_final_decision(self, report: str) -> str:
        """Format final trading decision for display"""
        if not report:
            return HTMLTemplateBuilder.create_placeholder("Final decision pending...")
        
        html_content = self._markdown_to_html(report)
        decision_summary = self._extract_decision_summary(report)
        
        formatted_content = f"""
        <div class='decision-summary'>
            {decision_summary}
        </div>
        <div class='decision-details'>
            {html_content}
        </div>
        """
        
        return HTMLTemplateBuilder.create_report_template(formatted_content, "⚖️ Final Trading Decision")
    
    
    def _markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML"""
        if not content:
            return ""
        
        # Simple markdown conversion
        html_content = content
        
        # Headers
        html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # Bold and italic
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        
        # Lists
        html_content = re.sub(r'^- (.*?)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html_content, flags=re.DOTALL)
        
        # Line breaks
        html_content = html_content.replace('\n', '<br>')
        
        return html_content
    
    def _enhance_tables(self, content: str) -> str:
        """Enhance table formatting with better styling"""
        # Look for table patterns and enhance them
        table_pattern = r'\|(.*?)\|'
        
        def replace_table(match):
            table_content = match.group(1)
            cells = [cell.strip() for cell in table_content.split('|')]
            return f"<tr>{''.join(f'<td>{cell}</td>' for cell in cells)}</tr>"
        
        content = re.sub(table_pattern, replace_table, content)
        
        # Wrap consecutive table rows in table tags
        content = re.sub(r'(<tr>.*?</tr>)', r'<table class="analysis-table">\1</table>', content, flags=re.DOTALL)
        
        return content
    
    def _format_news_items(self, content: str) -> str:
        """Format news items with special styling"""
        # Look for news item patterns
        news_pattern = r'### (.*?) \(source: (.*?)\)'
        
        def replace_news_item(match):
            headline = match.group(1)
            source = match.group(2)
            return f'''
            <div class="news-item">
                <div class="news-headline">{headline}</div>
                <div class="news-source">Source: {source}</div>
            </div>
            '''
        
        content = re.sub(news_pattern, replace_news_item, content)
        return content
    
    def _highlight_financial_metrics(self, content: str) -> str:
        """Highlight financial metrics and ratios"""
        # Common financial metrics patterns
        metrics_patterns = [
            (r'P/E[:\s]+([0-9.]+)', r'<span class="financial-metric">P/E: <strong>\1</strong></span>'),
            (r'P/S[:\s]+([0-9.]+)', r'<span class="financial-metric">P/S: <strong>\1</strong></span>'),
            (r'ROE[:\s]+([0-9.%]+)', r'<span class="financial-metric">ROE: <strong>\1</strong></span>'),
            (r'ROA[:\s]+([0-9.%]+)', r'<span class="financial-metric">ROA: <strong>\1</strong></span>'),
            (r'Revenue[:\s]+\$([0-9.,]+)', r'<span class="financial-metric">Revenue: <strong>$\1</strong></span>'),
            (r'Net Income[:\s]+\$([0-9.,]+)', r'<span class="financial-metric">Net Income: <strong>$\1</strong></span>'),
        ]
        
        for pattern, replacement in metrics_patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def _format_bull_bear_sections(self, content: str) -> str:
        """Format bull and bear researcher sections"""
        # Bull section
        content = re.sub(
            r'Bull Researcher.*?:(.*?)(?=Bear Researcher|$)',
            r'<div class="bull-section"><h3>🐂 Bull Researcher</h3><div class="argument-content">\1</div></div>',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Bear section
        content = re.sub(
            r'Bear Researcher.*?:(.*?)(?=Research Manager|$)',
            r'<div class="bear-section"><h3>🐻 Bear Researcher</h3><div class="argument-content">\1</div></div>',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Research Manager decision
        content = re.sub(
            r'Research Manager.*?:(.*?)$',
            r'<div class="manager-decision"><h3>👨‍💼 Research Manager Decision</h3><div class="decision-content">\1</div></div>',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        return content
    
    def _format_action_items(self, content: str) -> str:
        """Format action items in trading plan"""
        # Look for action items patterns
        action_patterns = [
            (r'Action[s]?:(.*?)(?=\n\n|$)', r'<div class="action-items"><h4>🎯 Actions</h4>\1</div>'),
            (r'Recommendation[s]?:(.*?)(?=\n\n|$)', r'<div class="recommendations"><h4>💡 Recommendations</h4>\1</div>'),
            (r'Risk[s]?:(.*?)(?=\n\n|$)', r'<div class="risks"><h4>⚠️ Risks</h4>\1</div>'),
        ]
        
        for pattern, replacement in action_patterns:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
        
        return content
    
    def _extract_decision_summary(self, content: str) -> str:
        """Extract key decision summary from final decision"""
        # Look for final decision patterns
        decision_patterns = [
            r'Final call[:\s]+(.*?)(?=\n|$)',
            r'Recommendation[:\s]+(.*?)(?=\n|$)',
            r'Decision[:\s]+(.*?)(?=\n|$)',
        ]
        
        for pattern in decision_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                decision = match.group(1).strip()
                
                # Determine decision type and color
                if "BUY" in decision.upper():
                    color = "#28a745"
                    icon = "📈"
                elif "SELL" in decision.upper():
                    color = "#dc3545"
                    icon = "📉"
                elif "HOLD" in decision.upper():
                    color = "#ffc107"
                    icon = "⏸️"
                else:
                    color = "#6c757d"
                    icon = "🤔"
                
                return f'''
                <div class="decision-highlight" style="background: {color}; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="font-size: 1.2em; font-weight: bold;">
                        {icon} {decision}
                    </div>
                </div>
                '''
        
        return ""
