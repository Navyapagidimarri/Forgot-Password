from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import OTPModel
from .serializers import SendOTPSerializer, VerifyOTPSerializer, CreateNewPasswordSerializer
import random
from django.core.mail import send_mail
from django.conf import settings


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    print(request.data)
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = str(random.randint(1000, 9999))
        otp_model, created = OTPModel.objects.get_or_create(email=email)
        otp_model.otp = otp
        otp_model.save()
        subject = 'Your OTP for Password Reset'
        message = f'Your OTP is: {otp}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        return Response({'detail': 'OTP sent successfully.'})
    else:
        return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user_otp = serializer.validated_data['otp']
        try:
            otp_model = OTPModel.objects.get(email=email)
        except OTPModel.DoesNotExist:
            return Response({'detail': 'Invalid email or OTP.'}, status=400)

        stored_otp = otp_model.otp
        if user_otp == stored_otp:
            return Response({'detail': 'OTP verification successful.'})
        else:
            return Response({'detail': 'Invalid OTP.'}, status=400)
    else:
        return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_new_password(request):
    serializer = CreateNewPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        token = serializer.validated_data.get('token') 
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=400)
        user.set_password(password)
        user.save()  
        OTPModel.objects.filter(email=email).delete()

        return Response({'detail': 'Password reset successfully.'})
    else:
        return Response(serializer.errors, status=400)
