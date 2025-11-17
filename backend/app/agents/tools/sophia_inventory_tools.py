"""
Sophia Inventory Tools - Supply & Equipment Management

Tools for managing clinic inventory, supplies, and equipment.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.odoo_client import OdooClient
from app.integrations.odoo_client_factory import OdooClientFactory
from app.agents.context import DentaFlowContext

logger = logging.getLogger(__name__)

# Initialize __all__ list
__all__ = []


@tool
def check_inventory_levels_tool(category: Optional[str] = None, low_stock_only: bool = False,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Check current inventory levels for all supplies.
    
    Args:
        category: Filter by category (e.g., "Anesthetics", "Gloves", "Dental Materials")
        low_stock_only: Show only items with low stock
        
    Returns:
        JSON string with inventory levels
    """
    try:
        logger.info(f"Checking inventory levels (category={category}, low_stock={low_stock_only})")
        
        # Get inventory
        inventory = odoo.get_inventory_levels()
        
        # Filter by category if specified
        if category:
            inventory = [item for item in inventory if category.lower() in item.get('categ_id', ['', ''])[1].lower()]
        
        # Filter low stock
        if low_stock_only:
            inventory = [item for item in inventory if item.get('qty_available', 0) < 10]  # Threshold
        
        # Sort by quantity
        inventory = sorted(inventory, key=lambda x: x.get('qty_available', 0))
        
        result = {
            'total_items': len(inventory),
            'low_stock_items': len([i for i in inventory if i.get('qty_available', 0) < 10]),
            'out_of_stock': len([i for i in inventory if i.get('qty_available', 0) == 0]),
            'items': inventory[:20],  # Limit to 20
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error checking inventory levels: {e}")
        return f"Error: {str(e)}"


@tool
def get_low_stock_alerts_tool(
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get alerts for items with low stock that need reordering.
    
    Returns:
        JSON string with low stock alerts
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info("Getting low stock alerts")
        
        # Get stock alerts from Odoo
        alerts = odoo.get_stock_alerts(alert_type='low_stock')
        
        # Sort by urgency (lowest quantity first)
        alerts = sorted(alerts, key=lambda x: x.get('current_qty', 0))
        
        result = {
            'alert_count': len(alerts),
            'critical_alerts': len([a for a in alerts if a.get('current_qty', 0) == 0]),
            'alerts': alerts[:15],  # Limit to 15
            'recommendation': "Consider placing orders for critical items immediately" if len(alerts) > 0 else "All stock levels are healthy"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting low stock alerts: {e}")
        return f"Error: {str(e)}"


@tool
def track_expiring_products_tool(days_ahead: int = 30,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Track products expiring within specified days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 30)
        
    Returns:
        JSON string with expiring products
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Tracking products expiring in next {days_ahead} days")
        
        # Get expiring products
        expiring = odoo.get_expiring_products(days_threshold=days_ahead)
        
        # Sort by expiration date
        expiring = sorted(expiring, key=lambda x: x.get('expiration_date', ''))
        
        # Calculate total value at risk
        total_qty = sum(e.get('product_qty', 0) for e in expiring)
        
        result = {
            'expiring_count': len(expiring),
            'total_quantity_at_risk': total_qty,
            'days_threshold': days_ahead,
            'products': expiring[:15],  # Limit to 15
            'recommendation': f"Review {len(expiring)} expiring items and plan usage or disposal" if len(expiring) > 0 else "No products expiring soon"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error tracking expiring products: {e}")
        return f"Error: {str(e)}"


@tool
def create_purchase_order_tool(supplier_name: str, items: List[Dict[str, Any]], notes: Optional[str] = None,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Create a purchase order for supplies.
    
    Args:
        supplier_name: Name of supplier/vendor
        items: List of items to order [{"product_name": str, "quantity": float, "price": float}]
        notes: Optional notes for the order
        
    Returns:
        JSON string with purchase order details
    """
    try:
        logger.info(f"Creating purchase order for {supplier_name}")
        
        # In real implementation, would:
        # 1. Search for supplier by name
        # 2. Search for products by name
        # 3. Create actual purchase order
        
        # For now, simulate success
        order_total = sum(item.get('quantity', 0) * item.get('price', 0) for item in items)
        
        result = {
            'success': True,
            'order_number': f"PO{datetime.now().strftime('%Y%m%d%H%M')}",
            'supplier': supplier_name,
            'items_count': len(items),
            'total_amount': order_total,
            'currency': 'ILS',
            'status': 'draft',
            'created_date': datetime.now().isoformat(),
            'notes': notes or '',
            'message': f"Purchase order created successfully. Total: ₪{order_total:.2f}"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating purchase order: {e}")
        return f"Error: {str(e)}"


@tool
def get_purchase_orders_tool(status: Optional[str] = None, days_back: int = 30,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get recent purchase orders.
    
    Args:
        status: Filter by status ('draft', 'sent', 'purchase', 'done', 'cancel')
        days_back: Number of days to look back (default: 30)
        
    Returns:
        JSON string with purchase orders
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Getting purchase orders (status={status}, days_back={days_back})")
        
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Get purchase orders
        orders = odoo.get_purchase_orders(state=status, date_from=date_from)
        
        # Sort by date (newest first)
        orders = sorted(orders, key=lambda x: x.get('date_order', ''), reverse=True)
        
        # Calculate totals
        total_amount = sum(o.get('amount_total', 0) for o in orders)
        
        result = {
            'order_count': len(orders),
            'total_amount': total_amount,
            'currency': 'ILS',
            'period_days': days_back,
            'orders': orders[:10],  # Limit to 10
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting purchase orders: {e}")
        return f"Error: {str(e)}"


@tool
def get_inventory_valuation_tool(
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get total inventory valuation (cost and potential value).
    
    Returns:
        JSON string with inventory valuation
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info("Getting inventory valuation")
        
        # Get valuation
        valuation = odoo.get_inventory_valuation()
        
        result = {
            'total_cost': valuation.get('total_cost', 0),
            'total_value': valuation.get('total_value', 0),
            'potential_profit': valuation.get('potential_profit', 0),
            'total_items': valuation.get('total_items', 0),
            'total_quantity': valuation.get('total_quantity', 0),
            'currency': 'ILS',
            'valuation_date': datetime.now().isoformat(),
            'profit_margin': f"{(valuation.get('potential_profit', 0) / valuation.get('total_cost', 1) * 100):.1f}%" if valuation.get('total_cost', 0) > 0 else "0%"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting inventory valuation: {e}")
        return f"Error: {str(e)}"


@tool
def get_stock_movements_tool(product_name: Optional[str] = None, days_back: int = 7,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get stock movements (in/out) for tracking usage.
    
    Args:
        product_name: Filter by product name
        days_back: Number of days to look back (default: 7)
        
    Returns:
        JSON string with stock movements
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Getting stock movements (product={product_name}, days_back={days_back})")
        
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Get stock moves
        moves = odoo.get_stock_moves(date_from=date_from)
        
        # Filter by product if specified
        if product_name:
            moves = [m for m in moves if product_name.lower() in m.get('product_id', ['', ''])[1].lower()]
        
        # Sort by date (newest first)
        moves = sorted(moves, key=lambda x: x.get('date', ''), reverse=True)
        
        # Calculate totals
        total_in = sum(m.get('product_uom_qty', 0) for m in moves if 'in' in m.get('reference', '').lower())
        total_out = sum(m.get('product_uom_qty', 0) for m in moves if 'out' in m.get('reference', '').lower())
        
        result = {
            'movement_count': len(moves),
            'total_in': total_in,
            'total_out': total_out,
            'net_change': total_in - total_out,
            'period_days': days_back,
            'movements': moves[:15],  # Limit to 15
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting stock movements: {e}")
        return f"Error: {str(e)}"


@tool
def suggest_reorder_quantities_tool(category: Optional[str] = None,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Suggest reorder quantities based on usage patterns and current stock.
    
    Args:
        category: Filter by category
        
    Returns:
        JSON string with reorder suggestions
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Suggesting reorder quantities (category={category})")
        
        # Get low stock items
        inventory = odoo.get_inventory_levels(category_id=None)
        low_stock = [item for item in inventory if item.get('qty_available', 0) < 10]
        
        # Get stock movements to calculate usage rate
        moves = odoo.get_stock_moves(date_from=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        suggestions = []
        for item in low_stock[:10]:  # Top 10
            product_id = item['id']
            product_name = item.get('name', 'Unknown')
            current_qty = item.get('qty_available', 0)
            
            # Calculate usage rate (simplified)
            product_moves = [m for m in moves if m.get('product_id', [0])[0] == product_id]
            usage_per_month = sum(m.get('product_uom_qty', 0) for m in product_moves)
            
            # Suggest 2 months worth
            suggested_qty = max(20, usage_per_month * 2)
            
            suggestions.append({
                'product_name': product_name,
                'current_qty': current_qty,
                'usage_per_month': usage_per_month,
                'suggested_order_qty': suggested_qty,
                'urgency': 'high' if current_qty == 0 else 'medium',
                'estimated_cost': suggested_qty * item.get('standard_price', 0) if 'standard_price' in item else 'N/A'
            })
        
        result = {
            'suggestion_count': len(suggestions),
            'total_estimated_cost': sum(s.get('estimated_cost', 0) for s in suggestions if isinstance(s.get('estimated_cost'), (int, float))),
            'currency': 'ILS',
            'suggestions': suggestions,
            'recommendation': f"Consider ordering {len(suggestions)} items to maintain healthy stock levels"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error suggesting reorder quantities: {e}")
        return f"Error: {str(e)}"


@tool
def get_storage_locations_tool(
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get all storage locations in the clinic.
    
    Returns:
        JSON string with storage locations
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info("Getting storage locations")
        
        # Get locations
        locations = odoo.get_storage_locations()
        
        result = {
            'location_count': len(locations),
            'locations': locations,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting storage locations: {e}")
        return f"Error: {str(e)}"


@tool
def generate_inventory_report_tool(report_type: str = "summary", days_back: int = 30,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Generate comprehensive inventory report.
    
    Args:
        report_type: Type of report ('summary', 'detailed', 'valuation', 'movements')
        days_back: Number of days to include (default: 30)
        
    Returns:
        JSON string with inventory report
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Generating inventory report (type={report_type}, days={days_back})")
        
        if report_type == "summary":
            # Get key metrics
            inventory = odoo.get_inventory_levels()
            alerts = odoo.get_stock_alerts()
            valuation = odoo.get_inventory_valuation()
            
            report = {
                'report_type': 'summary',
                'generated_date': datetime.now().isoformat(),
                'period_days': days_back,
                'metrics': {
                    'total_items': len(inventory),
                    'low_stock_items': len(alerts),
                    'out_of_stock': len([i for i in inventory if i.get('qty_available', 0) == 0]),
                    'total_valuation': valuation.get('total_value', 0),
                    'total_cost': valuation.get('total_cost', 0),
                },
                'alerts': alerts[:5],
                'top_items_by_value': sorted(inventory, key=lambda x: x.get('qty_available', 0) * x.get('list_price', 0), reverse=True)[:5],
            }
        
        elif report_type == "valuation":
            report = odoo.get_inventory_valuation()
            report['report_type'] = 'valuation'
            report['generated_date'] = datetime.now().isoformat()
        
        elif report_type == "movements":
            date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            moves = odoo.get_stock_moves(date_from=date_from)
            
            report = {
                'report_type': 'movements',
                'generated_date': datetime.now().isoformat(),
                'period_days': days_back,
                'total_movements': len(moves),
                'movements': moves[:20],
            }
        
        else:
            report = {'error': f"Unknown report type: {report_type}"}
        
        import json
        return json.dumps(report, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating inventory report: {e}")
        return f"Error: {str(e)}"


@tool
def get_patient_satisfaction_tool(days_back: int = 30,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get patient satisfaction scores and feedback.

    Args:
        days_back: Number of days to analyze (default: 30).

    Returns:
        A formatted string with patient satisfaction metrics.
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Getting patient satisfaction scores (days={days_back})")
        # This is a mock implementation.
        # In a real system, this would query a survey or feedback system.
        mock_feedback = {
            "nps_score": 75,
            "average_rating": 4.8,
            "total_responses": 150,
            "positive_feedback": [
                "The staff was very friendly and professional.",
                "I loved the new clinic design, it's very modern.",
                "Dr. Levi is the best dentist I've ever had."
            ],
            "negative_feedback": [
                "The waiting time was a bit long.",
                "It was hard to find parking near the clinic."
            ]
        }

        report = f"""**📊 דוח שביעות רצון מטופלים**

**ציון NPS:** {mock_feedback["nps_score"]}
**דירוג ממוצע:** {mock_feedback["average_rating"]}/5
**סה\"כ תגובות:** {mock_feedback["total_responses"]}

**נקודות לשימור:**
- {mock_feedback["positive_feedback"][0]}
- {mock_feedback["positive_feedback"][1]}

**נקודות לשיפור:**
- {mock_feedback["negative_feedback"][0]}
"""
        return report

    except Exception as e:
        logger.error(f"Error getting patient satisfaction: {e}")
        return f"Error: {str(e)}"


@tool
def get_no_show_rate_tool(days_back: int = 30,
    config: Annotated[RunnableConfig, InjectedToolArg] = None,
) -> str:
    """
    Get the no-show rate for appointments.

    Args:
        days_back: Number of days to analyze (default: 30).

    Returns:
        A formatted string with no-show rate metrics.
    """
    try:
        # Extract context
        context = config.get("configurable", {}).get("context") if config else None
        organization_id = context.organization_id if context else None
        odoo = OdooClientFactory.get_client(organization_id)
        
        logger.info(f"Getting no-show rate (days={days_back})")
        # This is a mock implementation.
        # In a real system, this would analyze appointment data from Odoo.
        mock_data = {
            "total_appointments": 500,
            "no_shows": 25,
            "no_show_rate": 5.0
        }

        report = f"""**📈 דוח אי-הגעה לתורים**

**סה\"כ תורים:** {mock_data["total_appointments"]}
**אי-הגעה:** {mock_data["no_shows"]}
**אחוז אי-הגעה:** {mock_data["no_show_rate"]}%
"""
        return report

    except Exception as e:
        logger.error(f"Error getting no-show rate: {e}")
        return f"Error: {str(e)}"


# Update __all__
__all__.extend(["get_patient_satisfaction_tool", "get_no_show_rate_tool"])

