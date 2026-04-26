"""
Model Enums
"""

import enum

from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum, JSON

from api.database.sql_database import sql_database

# +++++++++++++++++++++ data ++++++++++++++++++++
is_sqlite = sql_database.async_engine.url.get_backend_name() == "sqlite"

json_data_type = JSON if is_sqlite else postgresql.JSONB


# +++++++++++++++++++++++ user enum ++++++++++++++++++++++++++
class UserProviderEnum(enum.Enum):
    """
    UserProviderEnum
    """

    GOOGLE = "google"
    APPLE = "apple"
    STARTINBOX = "startinbox"
    GITHUB = "github"
    FACEBOOK = "facebook"
    TWITTER = "twitter"


postgres_user_provider_enum = postgresql.ENUM(
    UserProviderEnum,
    name="si_user_provider_enum",
    values_callable=lambda obj: [e.value for e in obj],
    create_type=False,  # Don't auto-create in migrations
)
sqlite_user_provider_enum = Enum(
    UserProviderEnum,
    name="si_user_provider_enum",
    values_callable=lambda obj: [e.value for e in obj],
)


class UserRoleEnum(enum.Enum):
    """
    UserRoleEnum
    """

    REGULAR = "regular"
    ADMIN = "admin"


postgres_user_role_enum = postgresql.ENUM(
    UserRoleEnum,
    name="si_user_role_enum",
    values_callable=lambda obj: [e.value for e in obj],
    create_type=False,  # Don't auto-create in migrations
)
sqlite_user_role_enum = Enum(
    UserRoleEnum,
    name="si_user_role_enum",
    values_callable=lambda obj: [e.value for e in obj],
)


# +++++++++++++++++++++ payment status enum +++++++++++++++++++++++++
class PaymentStatusEnum(str, enum.Enum):
    """
    PaymentStatus
    """

    PENDING = "pending"  # stripe
    SUCCESS = "success"  # flutterwave and paystack
    SUCCESSFUL = "successful"  # flutterwave
    FAILED = "failed"  # all
    REFUNDED = "refunded"  # all
    PAID = "paid"  # stripe
    UNPAID = "unpaid"  # stripe
    APPROVED = "approved"  # flutterwave
    CANCELLED = "cancelled"
    NOT_FOUND = "not_found"
    NO_PAYMENT_REQUIRED = "no_payment_required"  # stripe
    ABANDONED = "abandoned"  # paystack


postgres_payment_status_enum = postgresql.ENUM(
    PaymentStatusEnum,
    name="si_payment_status_enum",
    values_callable=lambda obj: [e.value for e in obj],
    create_type=False,  # Don't auto-create in migrations
)
sqlite_payment_status_enum = Enum(
    PaymentStatusEnum,
    name="si_payment_status_enum",
    values_callable=lambda obj: [e.value for e in obj],
)
# +++++++++++++++++++++ payment provider enum +++++++++++++++++++++++++


class PaymentProviderEnum(enum.Enum):
    """
    PaymentProviderEnum
    """

    STRIPE = "stripe"
    PAYSTACK = "paystack"
    FLUTTERWAVE = "flutterwave"
    PAYPAL = "paypal"


postgres_payment_provider_enum = postgresql.ENUM(
    PaymentProviderEnum,
    name="si_payment_provider_enum",
    values_callable=lambda obj: [e.value for e in obj],
    create_type=False,  # Don't auto-create in migrations
)
sqlite_payment_provider_enum = Enum(
    PaymentProviderEnum,
    name="si_payment_provider_enum",
    values_callable=lambda obj: [e.value for e in obj],
)
# +++++++++++++++++++++ subscription type enum +++++++++++++++++++++++++

class SubscriptionPlanTypeEnum(enum.Enum):
    """
    SubscriptionPlanTypeEnum
    """

    ONEOFF = "oneoff"
    REOCCURRING = "reoccurring"


postgres_subscription_type_enum = postgresql.ENUM(
    SubscriptionPlanTypeEnum,
    name="si_subscription_type_enum",
    values_callable=lambda obj: [e.value for e in obj],
    create_type=False,  # Don't auto-create in migrations
)
sqlite_subscription_type_enum = Enum(
    SubscriptionPlanTypeEnum,
    name="si_subscription_type_enum",
    values_callable=lambda obj: [e.value for e in obj],
)
