from django.views.generic import TemplateView
from rest_framework import generics
from rest_framework import viewsets
from .models import Post, User
from .serializers import PostSerializer, UserRegisterSerializer
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views import View


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == 'list':
            return []
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        serializer.save()


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    def post(self, request):
        url = "http://localhost:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Subscription Service',
                        },
                        'unit_amount': 5000,  # Цена в центах (например, 50.00 USD)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url + '/success/',
            cancel_url=url + '/cancel/',
        )
        return Response({'id': checkout_session.id})

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class StripeWebhook(View):
    def post(self, request):
        payload = request.body
        signature = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, signature, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return JsonResponse({'error': str(e)}, status=400)

        # Обработка различных событий
        if event['type'] == 'checkout.session.completed':
            checkout_session = event['data']['object']
            # Получаем данные о пользователе из сессии
            customer_email = checkout_session['customer_email']
            subscription_status = checkout_session['subscription_status']

            # Обновляем запись пользователя в базе данных
            try:
                user = User.objects.get(email=customer_email)
                user.subscription_status = subscription_status
                user.save()
            except User.DoesNotExist:
                # Создаем новую запись пользователя, если она не существует
                user = User(email=customer_email, subscription_status=subscription_status)
                user.save()

            return JsonResponse({'status': 'success'}, status=200)


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"
