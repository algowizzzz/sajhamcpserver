"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Limits vs Exposure Analysis Tool - MCP Tool Implementation
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from ..base_mcp_tool import BaseMCPTool


class LimitsExposureAnalysisTool(BaseMCPTool):
    """
    Comprehensive counterparty limits and exposure analysis tool
    
    Features:
    - Analyzes counterparty limit utilization and breaches
    - Provides detailed trade exposure breakdown
    - Aggregates risk metrics and statistics
    - Utilizes DuckDB OLAP tool for data querying
    """
    
    def __init__(self, config: Dict = None):
        """Initialize Limits vs Exposure Analysis Tool"""
        default_config = {
            'name': 'limits_exposure_analysis',
            'description': 'Comprehensive counterparty limits and exposure analysis',
            'version': '1.0.0',
            'enabled': True
        }
        if config:
            default_config.update(config)
        super().__init__(default_config)
        
        # Initialize DuckDB tool for data access
        self.duckdb_tool = None
        self._init_duckdb_tool()
    
    def _init_duckdb_tool(self):
        """Initialize DuckDB OLAP tool"""
        try:
            from .duckdb_olap_tools_tool import DuckDbOlapToolsTool
            
            duckdb_config = {
                'name': 'duckdb_olap_tools',
                'data_directory': 'data/duckdb',
                'enabled': True
            }
            self.duckdb_tool = DuckDbOlapToolsTool(duckdb_config)
            self.logger.info("DuckDB tool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize DuckDB tool: {e}")
            self.duckdb_tool = None
    
    def get_input_schema(self) -> Dict:
        """Get input schema for Limits vs Exposure Analysis"""
        return {
            "type": "object",
            "properties": {
                "counterparty_identifier": {
                    "type": "string",
                    "description": "Customer name or Adaptiv code to analyze"
                },
                "include_sections": {
                    "type": "array",
                    "description": "Specific sections to include (optional, defaults to all)",
                    "items": {
                        "type": "string",
                        "enum": [
                            "overview",
                            "limit_status",
                            "trade_summary",
                            "mtm_pnl",
                            "asset_class_breakdown",
                            "product_breakdown",
                            "collateral_status",
                            "desk_distribution",
                            "maturity_profile",
                            "risk_greeks",
                            "failed_trades",
                            "recent_activity",
                            "currency_exposure",
                            "risk_factors",
                            "combined_view",
                            "historical_limits"
                        ]
                    }
                }
            },
            "required": ["counterparty_identifier"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Any:
        """
        Execute comprehensive counterparty analysis
        
        Args:
            arguments: Tool arguments containing counterparty_identifier
            
        Returns:
            Comprehensive analysis report
        """
        if not self.duckdb_tool:
            return {
                'error': 'DuckDB tool not available',
                'note': 'Cannot perform analysis without DuckDB'
            }
        
        counterparty_id = arguments.get('counterparty_identifier')
        if not counterparty_id:
            raise ValueError("'counterparty_identifier' is required")
        
        include_sections = arguments.get('include_sections', [])
        
        # If no sections specified, include all
        if not include_sections:
            include_sections = [
                "overview", "limit_status", "trade_summary", "mtm_pnl",
                "asset_class_breakdown", "product_breakdown", "collateral_status",
                "desk_distribution", "maturity_profile", "risk_greeks",
                "failed_trades", "recent_activity", "currency_exposure",
                "risk_factors", "combined_view", "historical_limits"
            ]
        
        self.logger.info(f"Analyzing counterparty: {counterparty_id}")
        
        # Build comprehensive report
        report = {
            'counterparty_identifier': counterparty_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Execute each section
        for section in include_sections:
            try:
                section_data = self._execute_section(section, counterparty_id)
                report['sections'][section] = section_data
            except Exception as e:
                self.logger.error(f"Error in section {section}: {e}")
                report['sections'][section] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Add summary
        report['summary'] = self._generate_summary(report)
        
        return report
    
    def _execute_section(self, section: str, counterparty_id: str) -> Dict:
        """Execute a specific analysis section"""
        
        if section == "overview":
            return self._get_overview(counterparty_id)
        elif section == "limit_status":
            return self._get_limit_status(counterparty_id)
        elif section == "trade_summary":
            return self._get_trade_summary(counterparty_id)
        elif section == "mtm_pnl":
            return self._get_mtm_pnl_analysis(counterparty_id)
        elif section == "asset_class_breakdown":
            return self._get_asset_class_breakdown(counterparty_id)
        elif section == "product_breakdown":
            return self._get_product_breakdown(counterparty_id)
        elif section == "collateral_status":
            return self._get_collateral_status(counterparty_id)
        elif section == "desk_distribution":
            return self._get_desk_distribution(counterparty_id)
        elif section == "maturity_profile":
            return self._get_maturity_profile(counterparty_id)
        elif section == "risk_greeks":
            return self._get_risk_greeks(counterparty_id)
        elif section == "failed_trades":
            return self._get_failed_trades(counterparty_id)
        elif section == "recent_activity":
            return self._get_recent_activity(counterparty_id)
        elif section == "currency_exposure":
            return self._get_currency_exposure(counterparty_id)
        elif section == "risk_factors":
            return self._get_risk_factors(counterparty_id)
        elif section == "combined_view":
            return self._get_combined_view(counterparty_id)
        elif section == "historical_limits":
            return self._get_historical_limits(counterparty_id)
        else:
            return {'error': f'Unknown section: {section}'}
    
    def _execute_query(self, sql_query: str) -> Dict:
        """Execute SQL query via DuckDB tool"""
        try:
            result = self.duckdb_tool.execute({
                'action': 'query',
                'sql_query': sql_query,
                'limit': 10000
            })
            return result
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def _get_overview(self, counterparty_id: str) -> Dict:
        """Get counterparty overview from ccr_limits"""
        query = f"""
            SELECT 
                customer_name,
                adaptiv_code,
                sector,
                rating,
                country,
                region,
                portfolio,
                booking_location,
                risk_owner
            FROM ccr_limits 
            WHERE adaptiv_code = '{counterparty_id}' OR customer_name = '{counterparty_id}'
            LIMIT 1
        """
        result = self._execute_query(query)
        
        if result.get('row_count', 0) > 0:
            row = result['rows'][0]
            return {
                'customer_name': row[0],
                'adaptiv_code': row[1],
                'sector': row[2],
                'rating': row[3],
                'country': row[4],
                'region': row[5],
                'portfolio': row[6],
                'booking_location': row[7],
                'risk_owner': row[8]
            }
        return {'error': 'Counterparty not found'}
    
    def _get_limit_status(self, counterparty_id: str) -> Dict:
        """Get current limit status and exposures"""
        query = f"""
            SELECT 
                customer_name,
                limit_ccr,
                exposure_epe,
                exposure_pfe,
                exposure_ead,
                exposure_var,
                exposure_stress,
                limit_utilization_pct,
                limit_buffer,
                CASE 
                    WHEN limit_utilization_pct > 100 THEN 'BREACH'
                    WHEN limit_utilization_pct > 90 THEN 'WARNING'
                    ELSE 'OK'
                END as limit_status,
                as_of_date
            FROM ccr_limits 
            WHERE adaptiv_code = '{counterparty_id}' OR customer_name = '{counterparty_id}'
            ORDER BY as_of_date DESC
            LIMIT 1
        """
        result = self._execute_query(query)
        
        if result.get('row_count', 0) > 0:
            row = result['rows'][0]
            return {
                'customer_name': row[0],
                'limit_ccr': row[1],
                'exposure_epe': row[2],
                'exposure_pfe': row[3],
                'exposure_ead': row[4],
                'exposure_var': row[5],
                'exposure_stress': row[6],
                'limit_utilization_pct': row[7],
                'limit_buffer': row[8],
                'limit_status': row[9],
                'as_of_date': row[10]
            }
        return {'error': 'No limit data found'}
    
    def _get_trade_summary(self, counterparty_id: str) -> Dict:
        """Get trade count and notional summary"""
        query = f"""
            SELECT 
                counterparty,
                adaptiv_code,
                COUNT(*) as total_trades,
                COUNT(DISTINCT product) as unique_products,
                COUNT(DISTINCT asset_class) as unique_asset_classes,
                SUM(notional) as total_notional,
                AVG(notional) as avg_notional,
                MIN(notional) as min_notional,
                MAX(notional) as max_notional
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY counterparty, adaptiv_code
        """
        result = self._execute_query(query)
        
        if result.get('row_count', 0) > 0:
            row = result['rows'][0]
            return {
                'counterparty': row[0],
                'adaptiv_code': row[1],
                'total_trades': row[2],
                'unique_products': row[3],
                'unique_asset_classes': row[4],
                'total_notional': row[5],
                'avg_notional': row[6],
                'min_notional': row[7],
                'max_notional': row[8]
            }
        return {'error': 'No trade data found'}
    
    def _get_mtm_pnl_analysis(self, counterparty_id: str) -> Dict:
        """Get MTM and PnL analysis"""
        query = f"""
            SELECT 
                counterparty,
                SUM(mtm) as total_mtm,
                AVG(mtm) as avg_mtm,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                COUNT(CASE WHEN mtm > 0 THEN 1 END) as positive_mtm_count,
                COUNT(CASE WHEN mtm < 0 THEN 1 END) as negative_mtm_count,
                SUM(CASE WHEN mtm > 0 THEN mtm ELSE 0 END) as total_positive_mtm,
                SUM(CASE WHEN mtm < 0 THEN mtm ELSE 0 END) as total_negative_mtm
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY counterparty
        """
        result = self._execute_query(query)
        
        if result.get('row_count', 0) > 0:
            row = result['rows'][0]
            return {
                'counterparty': row[0],
                'total_mtm': row[1],
                'avg_mtm': row[2],
                'total_pnl': row[3],
                'avg_pnl': row[4],
                'positive_mtm_count': row[5],
                'negative_mtm_count': row[6],
                'total_positive_mtm': row[7],
                'total_negative_mtm': row[8]
            }
        return {'error': 'No MTM/PnL data found'}
    
    def _get_asset_class_breakdown(self, counterparty_id: str) -> Dict:
        """Get breakdown by asset class"""
        query = f"""
            SELECT 
                asset_class,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(mtm) as total_mtm,
                SUM(pnl) as total_pnl,
                AVG(notional) as avg_notional,
                COUNT(DISTINCT product) as product_count
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY asset_class
            ORDER BY total_notional DESC
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'asset_class': row[0],
                'trade_count': row[1],
                'total_notional': row[2],
                'total_mtm': row[3],
                'total_pnl': row[4],
                'avg_notional': row[5],
                'product_count': row[6]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_product_breakdown(self, counterparty_id: str) -> Dict:
        """Get breakdown by product"""
        query = f"""
            SELECT 
                product,
                asset_class,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(mtm) as total_mtm,
                ROUND(AVG(delta), 4) as avg_delta,
                ROUND(AVG(gamma), 4) as avg_gamma
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY product, asset_class
            ORDER BY total_notional DESC
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'product': row[0],
                'asset_class': row[1],
                'trade_count': row[2],
                'total_notional': row[3],
                'total_mtm': row[4],
                'avg_delta': row[5],
                'avg_gamma': row[6]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_collateral_status(self, counterparty_id: str) -> Dict:
        """Get collateral and netting analysis"""
        query = f"""
            SELECT 
                netting_set,
                csa_flag,
                collateralized,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(mtm) as total_mtm
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY netting_set, csa_flag, collateralized
            ORDER BY total_notional DESC
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'netting_set': row[0],
                'csa_flag': row[1],
                'collateralized': row[2],
                'trade_count': row[3],
                'total_notional': row[4],
                'total_mtm': row[5]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_desk_distribution(self, counterparty_id: str) -> Dict:
        """Get desk and book distribution"""
        query = f"""
            SELECT 
                desk,
                book,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(mtm) as total_mtm,
                COUNT(DISTINCT product) as products
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY desk, book
            ORDER BY total_notional DESC
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'desk': row[0],
                'book': row[1],
                'trade_count': row[2],
                'total_notional': row[3],
                'total_mtm': row[4],
                'products': row[5]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_maturity_profile(self, counterparty_id: str) -> Dict:
        """Get maturity profile analysis"""
        query = f"""
            SELECT 
                CASE 
                    WHEN maturity_date < '2026-01-01' THEN '< 1 Year'
                    WHEN maturity_date < '2027-01-01' THEN '1-2 Years'
                    WHEN maturity_date < '2028-01-01' THEN '2-3 Years'
                    ELSE '> 3 Years'
                END as maturity_bucket,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(mtm) as total_mtm
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY maturity_bucket
            ORDER BY maturity_bucket
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'maturity_bucket': row[0],
                'trade_count': row[1],
                'total_notional': row[2],
                'total_mtm': row[3]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_risk_greeks(self, counterparty_id: str) -> Dict:
        """Get risk Greeks analysis"""
        query = f"""
            SELECT 
                asset_class,
                SUM(delta) as total_delta,
                SUM(gamma) as total_gamma,
                SUM(vega) as total_vega,
                AVG(delta) as avg_delta,
                AVG(gamma) as avg_gamma,
                AVG(vega) as avg_vega,
                MIN(delta) as min_delta,
                MAX(delta) as max_delta
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY asset_class
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'asset_class': row[0],
                'total_delta': row[1],
                'total_gamma': row[2],
                'total_vega': row[3],
                'avg_delta': row[4],
                'avg_gamma': row[5],
                'avg_vega': row[6],
                'min_delta': row[7],
                'max_delta': row[8]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_failed_trades(self, counterparty_id: str) -> Dict:
        """Get failed or problematic trades"""
        query = f"""
            SELECT 
                trade_id,
                product,
                asset_class,
                notional,
                mtm,
                trade_date,
                maturity_date,
                failed_trade
            FROM trades 
            WHERE (adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}')
              AND failed_trade = TRUE
        """
        result = self._execute_query(query)
        
        failed_trades = []
        for row in result.get('rows', []):
            failed_trades.append({
                'trade_id': row[0],
                'product': row[1],
                'asset_class': row[2],
                'notional': row[3],
                'mtm': row[4],
                'trade_date': row[5],
                'maturity_date': row[6],
                'failed_trade': row[7]
            })
        
        return {'failed_trades': failed_trades, 'count': len(failed_trades)}
    
    def _get_recent_activity(self, counterparty_id: str) -> Dict:
        """Get recent trading activity"""
        query = f"""
            SELECT 
                trade_id,
                product,
                asset_class,
                notional,
                mtm,
                pnl,
                trade_date,
                maturity_date,
                desk,
                book
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            ORDER BY trade_date DESC
            LIMIT 10
        """
        result = self._execute_query(query)
        
        recent_trades = []
        for row in result.get('rows', []):
            recent_trades.append({
                'trade_id': row[0],
                'product': row[1],
                'asset_class': row[2],
                'notional': row[3],
                'mtm': row[4],
                'pnl': row[5],
                'trade_date': row[6],
                'maturity_date': row[7],
                'desk': row[8],
                'book': row[9]
            })
        
        return {'recent_trades': recent_trades, 'count': len(recent_trades)}
    
    def _get_currency_exposure(self, counterparty_id: str) -> Dict:
        """Get currency exposure breakdown"""
        query = f"""
            SELECT 
                currency,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(mtm) as total_mtm,
                SUM(pnl) as total_pnl
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY currency
        """
        result = self._execute_query(query)
        
        breakdown = []
        for row in result.get('rows', []):
            breakdown.append({
                'currency': row[0],
                'trade_count': row[1],
                'total_notional': row[2],
                'total_mtm': row[3],
                'total_pnl': row[4]
            })
        
        return {'breakdown': breakdown, 'count': len(breakdown)}
    
    def _get_risk_factors(self, counterparty_id: str) -> Dict:
        """Get top risk factors"""
        query = f"""
            SELECT 
                risk_factor,
                COUNT(*) as trade_count,
                SUM(notional) as total_notional,
                SUM(ABS(delta)) as total_abs_delta
            FROM trades 
            WHERE adaptiv_code = '{counterparty_id}' OR counterparty = '{counterparty_id}'
            GROUP BY risk_factor
            ORDER BY total_notional DESC
            LIMIT 10
        """
        result = self._execute_query(query)
        
        risk_factors = []
        for row in result.get('rows', []):
            risk_factors.append({
                'risk_factor': row[0],
                'trade_count': row[1],
                'total_notional': row[2],
                'total_abs_delta': row[3]
            })
        
        return {'risk_factors': risk_factors, 'count': len(risk_factors)}
    
    def _get_combined_view(self, counterparty_id: str) -> Dict:
        """Get combined view of trades vs limits"""
        query = f"""
            SELECT 
                c.customer_name,
                c.adaptiv_code,
                c.limit_ccr,
                c.exposure_epe,
                c.exposure_pfe,
                c.limit_utilization_pct,
                COUNT(t.trade_id) as active_trades,
                SUM(t.notional) as total_trade_notional,
                SUM(t.mtm) as total_trade_mtm,
                ROUND(c.exposure_epe / COUNT(t.trade_id), 2) as avg_exposure_per_trade
            FROM ccr_limits c
            LEFT JOIN trades t ON c.adaptiv_code = t.adaptiv_code
            WHERE c.adaptiv_code = '{counterparty_id}' OR c.customer_name = '{counterparty_id}'
            GROUP BY c.customer_name, c.adaptiv_code, c.limit_ccr, 
                     c.exposure_epe, c.exposure_pfe, c.limit_utilization_pct
        """
        result = self._execute_query(query)
        
        if result.get('row_count', 0) > 0:
            row = result['rows'][0]
            return {
                'customer_name': row[0],
                'adaptiv_code': row[1],
                'limit_ccr': row[2],
                'exposure_epe': row[3],
                'exposure_pfe': row[4],
                'limit_utilization_pct': row[5],
                'active_trades': row[6],
                'total_trade_notional': row[7],
                'total_trade_mtm': row[8],
                'avg_exposure_per_trade': row[9]
            }
        return {'error': 'No combined data found'}
    
    def _get_historical_limits(self, counterparty_id: str) -> Dict:
        """Get historical limit utilization"""
        query = f"""
            SELECT 
                as_of_date,
                exposure_epe,
                exposure_pfe,
                limit_ccr,
                limit_utilization_pct,
                limit_buffer
            FROM ccr_limits 
            WHERE adaptiv_code = '{counterparty_id}' OR customer_name = '{counterparty_id}'
            ORDER BY as_of_date DESC
            LIMIT 30
        """
        result = self._execute_query(query)
        
        history = []
        for row in result.get('rows', []):
            history.append({
                'as_of_date': row[0],
                'exposure_epe': row[1],
                'exposure_pfe': row[2],
                'limit_ccr': row[3],
                'limit_utilization_pct': row[4],
                'limit_buffer': row[5]
            })
        
        return {'history': history, 'count': len(history)}
    
    def _generate_summary(self, report: Dict) -> Dict:
        """Generate executive summary from report"""
        summary = {
            'counterparty': report.get('counterparty_identifier'),
            'analysis_timestamp': report.get('analysis_timestamp')
        }
        
        # Extract key metrics
        sections = report.get('sections', {})
        
        if 'overview' in sections:
            overview = sections['overview']
            summary['customer_name'] = overview.get('customer_name')
            summary['rating'] = overview.get('rating')
            summary['sector'] = overview.get('sector')
        
        if 'limit_status' in sections:
            limit_status = sections['limit_status']
            summary['limit_status'] = limit_status.get('limit_status')
            summary['limit_utilization_pct'] = limit_status.get('limit_utilization_pct')
            summary['exposure_epe'] = limit_status.get('exposure_epe')
        
        if 'trade_summary' in sections:
            trade_summary = sections['trade_summary']
            summary['total_trades'] = trade_summary.get('total_trades')
            summary['total_notional'] = trade_summary.get('total_notional')
        
        if 'mtm_pnl' in sections:
            mtm_pnl = sections['mtm_pnl']
            summary['total_mtm'] = mtm_pnl.get('total_mtm')
            summary['total_pnl'] = mtm_pnl.get('total_pnl')
        
        if 'failed_trades' in sections:
            failed_trades = sections['failed_trades']
            summary['failed_trades_count'] = failed_trades.get('count', 0)
        
        return summary

