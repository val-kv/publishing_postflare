from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from django.views.decorators.csrf import csrf_exempt
from .models import Post, User, Product
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from .serializers import UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == 'list':
            return []
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserRegistrationView(APIView):
    queryset = User.objects.all()

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = []

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        user = User.objects.filter(phone_number=phone_number).first()
        if user and user.check_password(password):
            return Response({'message': 'Успешный вход'})
        return Response({'message': 'Неправильный номер телефона или пароль'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    def post(self, request):
        # В DRF нет встроенной поддержки выхода из системы, поэтому мы просто возвращаем сообщение
        return Response({'message': 'Успешный выход'})


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id=product_id)
        url = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.name
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            },
            mode='payment',
            success_url=url + '/success/',
            cancel_url=url + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class ProtectedView(TemplateView):
    template_name = "protected_page.html"


class HomePageView(TemplateView):
    template_name = "index.html"


class PremiumView(TemplateView):
    template_name = "premium.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="Премиум подписка")
        context = super(PremiumView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        # send email to the customer
        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. The URL is: {product.url}",
            recipient_list=[customer_email],
            from_email="your@email.com"
        )

    return HttpResponse(status=200)
