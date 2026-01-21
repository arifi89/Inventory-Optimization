"""
Inventory optimization calculations: EOQ, ROP, Safety Stock
"""

import pandas as pd
import numpy as np
from scipy import stats


def calculate_eoq(annual_demand, ordering_cost, holding_cost):
    """
    Calculate Economic Order Quantity
    
    Args:
        annual_demand: Annual demand in units
        ordering_cost: Cost per order
        holding_cost: Annual holding cost per unit
        
    Returns:
        EOQ value
    """
    pass


def calculate_rop(daily_demand, lead_time_days, safety_stock=0):
    """
    Calculate Reorder Point
    
    Args:
        daily_demand: Average daily demand
        lead_time_days: Lead time in days
        safety_stock: Safety stock quantity
        
    Returns:
        ROP value
    """
    pass


def calculate_safety_stock(demand_std, lead_time_days, service_level=0.95):
    """
    Calculate Safety Stock
    
    Args:
        demand_std: Standard deviation of demand
        lead_time_days: Lead time in days
        service_level: Desired service level (e.g., 0.95 for 95%)
        
    Returns:
        Safety stock quantity
    """
    pass
