from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from base.models import Pupil
from api_serializers.base_serializsers import PupilSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from base.models import CustomUser
from rest_framework.views import APIView


class PupilListCreateView(generics.ListCreateAPIView):
    """
    O'quvchilar ro'yxatini ko'rish va yangi o'quvchi qo'shish uchun view.
    """
    queryset = Pupil.objects.all()
    serializer_class = PupilSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """
        O'quvchilar ro'yxatini olish.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Yangi o'quvchi yaratish.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class PupilRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pupil.objects.all()
    serializer_class = PupilSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        """
        O'quvchini ko'rish.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        O'quvchini yangilash.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        O'quvchini o'chirish.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Asosiy tokenni olish
        token = super().get_token(user)

        # Qo'shimcha ma'lumotlarni token ichiga kiritish
        token['username'] = user.username
        token['email'] = user.email
        token['user_type'] = user.user_type  # Foydalanuvchi turi (masalan, 'teacher', 'parent', 'pupil')

        return token





class LoginView(APIView):
    permission_classes = [permissions.AllowAny]  # Ruxsatlarni ochiq qilish

    def post(self, request, *args, **kwargs):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({'error': 'Username/Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if '@' in username_or_email:
            user = authenticate(request, email=username_or_email, password=password)
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_200_OK)








































