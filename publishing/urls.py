from django.urls import path, include
from rest_framework.routers import DefaultRouter

import publishing
from .views import PostViewSet, CreateCheckoutSession, CancelView, SuccessView, StripeWebhook, \
    HomePageView, ProtectedView, UserRegistrationView, UserLoginView, UserLogoutView

app_name = 'publishing'

router = DefaultRouter()
router.register(r'publishing', PostViewSet)

urlpatterns = [
    path('', HomePageView.as_view(), name='home', kwargs={'template_name': 'index.html'}),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('posts/', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='posts'),
    path('create-checkout-session/<int:pk>/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('webhook/', StripeWebhook.as_view(), name='stripe-webhook'),
]
