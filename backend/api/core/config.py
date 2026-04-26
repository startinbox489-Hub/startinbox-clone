"""
Env config module
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Class to access env variables
    """

    port: str
    test: str
    app_env: str
    app_name: str
    client_side_url: str

    db_url_sync: str
    db_url_test: str
    db_url_async: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_schema: str

    jwt_access_token_expiry: int
    jwt_refresh_token_expiry: int
    jwt_algorithm: str
    secrets: str
    jwt_secrets: str
    jwt_algorithm: str
    jwt_issuer: str
    jwt_audience: str

    mail_port: int
    mail_username: str
    mail_password: str
    mail_server: str

    redis_url: str = "redis://127.0.0.1:6379/0"

    google_client_id: str
    google_audience: str
    google_gemini_api_key: str
    google_gemini_model: str

    mailgun_api_key: str

    domain_name: str

    mailgun_base_url: str

    domain_email: str

    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str

    meta_whatsapp_token: str
    meta_phone_number_id: str
    meta_graph_url: str
    meta_app_id: str

    app_url: str

    url_secret: str

    flw_secret_key: str
    flw_public_key: str
    flw_encryption_key: str
    flw_payment_url: str = "https://api.flutterwave.com/v3/payments"
    flw_client_redirect_url: str
    flw_secret_hash: str

    stripe_api_secret_key: str
    frontend_stripe_success_url: str
    frontend_stripe_cancel_url: str
    stripe_webhook_secret: str

    send_grid_api_key: str
    send_grid_from_mail: str
    send_grid_mail_base_url: str

    paystack_secret_key: str
    paystack_base_url: str

    mailchimp_api_key: str
    mailchimp_audience_id: str
    mailchimp_base_url: str

    resend_mail_api_key: str = "somekey"
    resend_mail_default_email: str
    resend_mail_info_email: str

    pm_calendly_link: str

    meta_pixel_url: str
    meta_pixel_access_token: str
    meta_pixel_id: str

    admin_email: str
    support_email: str
    contact_email: str
    
    ipinfo_api_key: str

    model_config: SettingsConfigDict = {  # type: ignore
        "env_file": ".env",
        "case_sensitive": False,
    }


# Initialize settings
settings = Settings()  # type: ignore
