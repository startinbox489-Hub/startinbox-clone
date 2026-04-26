"""
app enums
"""

import enum


class FlutterwaveEvent(str, enum.Enum):
    """
    FlutterwaveEvents
    """

    CHARGE_COMPLETE = "charge.completed"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SUBSCRIPTION_EXPIRED = "subscription.expired"
    INVOICE_CREATED = "invoice.created"
