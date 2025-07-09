import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import markdown
import html

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
            return "<div class='report-placeholder'>Market analysis pending...</div>"
        
        return self._format_report_with_tables(report, "📈 Market Analysis")
    
    def format_sentiment_report(self, report: str) -> str:
        """Format social sentiment report for display"""
        if not report:
            return "<div class='report-placeholder'>Social sentiment analysis pending...</div>"
        
        return self._format_report_basic(report, "📱 Social Sentiment Analysis")
    
    def format_news_report(self, report: str) -> str:
        """Format news analysis report for display"""
        if not report:
            return "<div class='report-placeholder'>News analysis pending...</div>"
        
        return self._format_report_with_news_items(report, "📰 News Analysis")
    
    def format_fundamentals_report(self, report: str) -> str:
        """Format fundamentals analysis report for display"""
        if not report:
            return "<div class='report-placeholder'>Fundamentals analysis pending...</div>"
        
        return self._format_report_with_financials(report, "💼 Fundamentals Analysis")
    
    def format_research_decision(self, report: str) -> str:
        """Format research team decision for display"""
        if not report:
            return "<div class='report-placeholder'>Research team decision pending...</div>"
        
        return self._format_research_debate(report, "🎯 Research Team Decision")
    
    def format_trading_plan(self, report: str) -> str:
        """Format trading plan for display"""
        if not report:
            return "<div class='report-placeholder'>Trading plan pending...</div>"
        
        return self._format_trading_plan_detailed(report, "💰 Trading Plan")
    
    def format_final_decision(self, report: str) -> str:
        """Format final trading decision for display"""
        if not report:
            return "<div class='report-placeholder'>Final decision pending...</div>"
        
        return self._format_final_decision_detailed(report, "⚖️ Final Trading Decision")
    
    def _format_report_basic(self, content: str, title: str) -> str:
        """Basic report formatting with markdown support"""
        html_content = self._markdown_to_html(content)
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {html_content}
            </div>
        </div>
        """
    
    def _format_report_with_tables(self, content: str, title: str) -> str:
        """Format report with enhanced table rendering"""
        html_content = self._markdown_to_html(content)
        
        # Enhanced table formatting
        html_content = self._enhance_tables(html_content)
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {html_content}
            </div>
        </div>
        """
    
    def _format_report_with_news_items(self, content: str, title: str) -> str:
        """Format news report with special news item styling"""
        html_content = self._markdown_to_html(content)
        
        # Format news items specially
        html_content = self._format_news_items(html_content)
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {html_content}
            </div>
        </div>
        """
    
    def _format_report_with_financials(self, content: str, title: str) -> str:
        """Format fundamentals report with financial metrics highlighting"""
        html_content = self._markdown_to_html(content)
        
        # Highlight financial metrics
        html_content = self._highlight_financial_metrics(html_content)
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {html_content}
            </div>
        </div>
        """
    
    def _format_research_debate(self, content: str, title: str) -> str:
        """Format research team debate with bull/bear sections"""
        html_content = self._markdown_to_html(content)
        
        # Format bull/bear sections
        html_content = self._format_bull_bear_sections(html_content)
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {html_content}
            </div>
        </div>
        """
    
    def _format_trading_plan_detailed(self, content: str, title: str) -> str:
        """Format trading plan with action items and risk metrics"""
        html_content = self._markdown_to_html(content)
        
        # Extract and format action items
        html_content = self._format_action_items(html_content)
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {html_content}
            </div>
        </div>
        """
    
    def _format_final_decision_detailed(self, content: str, title: str) -> str:
        """Format final decision with decision highlights"""
        html_content = self._markdown_to_html(content)
        
        # Extract decision summary
        decision_summary = self._extract_decision_summary(content)
        
        formatted_content = f"""
        <div class='decision-summary'>
            {decision_summary}
        </div>
        <div class='decision-details'>
            {html_content}
        </div>
        """
        
        return f"""
        <div class='report-container'>
            <div class='report-header'>
                <h2>{title}</h2>
                <div class='report-timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class='report-content'>
                {formatted_content}
            </div>
        </div>
        """
    
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
    
    def format_progress_update(self, progress_data: Dict[str, Any]) -> str:
        """Format progress update for live display"""
        if not progress_data:
            return "<div>No progress data available</div>"
        
        agent_status = progress_data.get("agent_status", {})
        ticker = progress_data.get("ticker", "Unknown")
        date = progress_data.get("date", "Unknown")
        
        # Calculate progress percentage
        total_agents = len(agent_status)
        completed = sum(1 for status in agent_status.values() if status == "completed")
        percentage = int((completed / total_agents) * 100) if total_agents > 0 else 0
        
        # Create progress bar
        progress_bar = f'''
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {percentage}%"></div>
            <div class="progress-text">{percentage}% Complete</div>
        </div>
        '''
        
        # Create team status
        team_status = self._format_team_status_compact(agent_status)
        
        return f'''
        <div class="progress-update">
            <h3>Analysis Progress: {ticker} ({date})</h3>
            {progress_bar}
            {team_status}
        </div>
        '''
    
    def _format_team_status_compact(self, agent_status: Dict[str, str]) -> str:
        """Format team status in compact view"""
        teams = {
            "Analysts": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
            "Research": ["Bull Researcher", "Bear Researcher", "Research Manager"],
            "Trading": ["Trader"],
            "Risk Mgmt": ["Risky Analyst", "Safe Analyst", "Neutral Analyst"],
            "Portfolio": ["Portfolio Manager"],
        }
        
        html = '<div class="team-status-compact">'
        
        for team_name, agents in teams.items():
            team_completed = sum(1 for agent in agents if agent_status.get(agent) == "completed")
            team_total = len(agents)
            team_percentage = int((team_completed / team_total) * 100) if team_total > 0 else 0
            
            html += f'''
            <div class="team-item">
                <div class="team-name">{team_name}</div>
                <div class="team-progress">
                    <div class="team-progress-bar" style="width: {team_percentage}%"></div>
                    <div class="team-progress-text">{team_completed}/{team_total}</div>
                </div>
            </div>
            '''
        
        html += '</div>'
        return html
    
    def format_error(self, error_message: str) -> str:
        """Format error message for display"""
        return f'''
        <div class="error-container">
            <div class="error-header">
                <h3>❌ Error</h3>
            </div>
            <div class="error-content">
                {html.escape(error_message)}
            </div>
        </div>
        '''
    
    def create_summary_report(self, final_state: Dict[str, Any]) -> str:
        """Create a comprehensive summary report"""
        if not final_state:
            return "<div>No final state available</div>"
        
        ticker = final_state.get("company_of_interest", "Unknown")
        date = final_state.get("trade_date", "Unknown")
        
        html = f'''
        <div class="summary-report">
            <div class="summary-header">
                <h2>📊 Analysis Summary: {ticker}</h2>
                <div class="summary-date">Date: {date}</div>
            </div>
        '''
        
        # Add quick summary cards
        summary_cards = self._create_summary_cards(final_state)
        html += summary_cards
        
        # Add detailed sections
        for section in ["market_report", "sentiment_report", "news_report", "fundamentals_report"]:
            if section in final_state and final_state[section]:
                title = self.report_titles.get(section, section.replace("_", " ").title())
                html += f'''
                <div class="summary-section">
                    <h3>{title}</h3>
                    <div class="summary-content">
                        {self._truncate_content(final_state[section], 300)}
                    </div>
                </div>
                '''
        
        html += '</div>'
        return html
    
    def _create_summary_cards(self, final_state: Dict[str, Any]) -> str:
        """Create summary cards for key metrics"""
        cards = []
        
        # Decision card
        final_decision = final_state.get("final_trade_decision", "")
        if final_decision:
            decision_type = "UNKNOWN"
            if "BUY" in final_decision.upper():
                decision_type = "BUY"
                color = "#28a745"
            elif "SELL" in final_decision.upper():
                decision_type = "SELL"
                color = "#dc3545"
            elif "HOLD" in final_decision.upper():
                decision_type = "HOLD"
                color = "#ffc107"
            else:
                color = "#6c757d"
            
            cards.append(f'''
            <div class="summary-card" style="border-left: 4px solid {color};">
                <div class="card-title">Final Decision</div>
                <div class="card-value" style="color: {color};">{decision_type}</div>
            </div>
            ''')
        
        # Reports count
        reports_count = sum(1 for key in ["market_report", "sentiment_report", "news_report", "fundamentals_report"] 
                           if final_state.get(key))
        cards.append(f'''
        <div class="summary-card">
            <div class="card-title">Reports Generated</div>
            <div class="card-value">{reports_count}/4</div>
        </div>
        ''')
        
        return f'<div class="summary-cards">{"".join(cards)}</div>'
    
    def _truncate_content(self, content: str, max_length: int) -> str:
        """Truncate content to specified length"""
        if len(content) <= max_length:
            return content
        
        truncated = content[:max_length]
        # Try to break at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            truncated = truncated[:last_space]
        
        return truncated + "..."