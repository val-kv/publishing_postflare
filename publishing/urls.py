from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CreateCheckoutSession, UserRegisterView, CancelView, SuccessView, StripeWebhook

app_name = 'publishing'

router = DefaultRouter()
router.register(r'publishing', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('posts/', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='posts'),
    path('create-checkout-session/<int:pk>/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('webhook/', StripeWebhook.as_view(), name='stripe-webhook'),
]
