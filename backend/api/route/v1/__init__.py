"""
Routes
"""

from fastapi import APIRouter

from api.route.v1.subscription_plan_route import sub_plan_router
from api.route.v1.auth_route import auth_router
from api.route.v1.news_letter_route import news_letter_router
from api.route.v1.faq_route import faqs_router
from api.route.v1.startup_ideas_route import startup_ideas
from api.route.v1.reports_route import reports_router
from api.route.v1.payments_route import payment_route
from api.route.v1.adds_on_route import adds_on_router
from api.route.v1.testimonial_route import testimonials_router
from api.route.v1.idea_next_step_route import idea_next_step_router
from api.route.v1.blog_posts_route import blog_post_router
from api.route.v1.admin_blog_post_route import admin_blog_post_router
from api.route.v1.health_route import health_router

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth_router)
api_version_one.include_router(startup_ideas)
api_version_one.include_router(idea_next_step_router)
api_version_one.include_router(sub_plan_router)
api_version_one.include_router(news_letter_router)
api_version_one.include_router(faqs_router)
api_version_one.include_router(reports_router)
api_version_one.include_router(payment_route)
api_version_one.include_router(adds_on_router)
api_version_one.include_router(testimonials_router)
api_version_one.include_router(blog_post_router)
api_version_one.include_router(admin_blog_post_router)
api_version_one.include_router(health_router)
