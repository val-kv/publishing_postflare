from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CancelView, SuccessView, stripe_webhook, \
    HomePageView, ProtectedView, UserRegistrationView, UserLoginView, UserLogoutView, PremiumView, \
    CreateCheckoutSessionView

app_name = 'publishing'

router = DefaultRouter()
router.register(r'publishing', PostViewSet)

urlpatterns = [
    path('', HomePageView.as_view(), name='home', kwargs={'template_name': 'index.html'}),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('posts/', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='posts'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('premium/', PremiumView.as_view(), name='premium'),
]
