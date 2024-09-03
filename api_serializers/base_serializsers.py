from rest_framework import serializers
from django.contrib.auth import get_user_model
from base.models import Teacher, Pupil, Parent, Administrator
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model


User = get_user_model()

CustomUser = get_user_model()



from rest_framework import serializers
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class PupilRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=10)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    age = serializers.IntegerField()
    address = serializers.CharField(max_length=255, allow_blank=True, required=False)
    gmail = serializers.EmailField(required=False)
    image = serializers.ImageField(required=False)
    status = serializers.ChoiceField(choices=Pupil.STATUS_CHOICES, default='active')
    user_type = serializers.CharField(read_only=True, default='pupil')

    class Meta:
        model = Pupil
        fields = [
            'username', 'first_name', 'last_name', 'phone_number', 'password',
            'age', 'address', 'gmail', 'image', 'status', 'user_type'
        ]


    def validate_phone_number(self, value):
        if Pupil.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon mavjud.")
        return value


    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'phone_number': validated_data.pop('phone_number'),
            'password': validated_data.pop('password'),
        }

        if CustomUser.objects.filter(phone_number=user_data['phone_number']).exists():
            raise serializers.ValidationError({'phone_number': 'Bu telefon raqam allaqachon mavjud.'})

        user = CustomUser.objects.create_user(**user_data)
        user.set_password(user_data['password'])
        user.save()

        pupil = Pupil.objects.create(user=user, **validated_data)
        return pupil


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError(_("Username kiritilishi kerak."))
        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError(_("Parol kiritilishi kerak."))
        if len(value) < 8:
            raise serializers.ValidationError(_("Parol uzunligi kamida 8 ta belgidan iborat bo'lishi kerak."))
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(_("Parol kamida bitta raqamni o'z ichiga olishi kerak."))
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError(_("Parol kamida bitta harfni o'z ichiga olishi kerak."))
        return value

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(_("Login yoki parol noto'g'ri."))

        attrs['user'] = user
        return attrs


class VerifyUsernameAndPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=2)
    current_password = serializers.CharField(write_only=True, min_length=6, max_length=68)

    class Meta:
        fields = ['username', 'current_password']

    def validate(self, attrs):
        username = attrs.get('username')
        current_password = attrs.get('current_password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(_("Foydalanuvchi bu username bilan topilmadi."))

        if not user.check_password(current_password):
            raise serializers.ValidationError(_("Joriy parol noto'g'ri."))

        return attrs

class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    confirm_password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['new_password', 'confirm_password', 'token', 'uidb64']

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(_("Yangi parollar mos kelmadi."))

        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            # Decode the user ID
            id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)

            # Check the validity of the token
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed(_('Parolni tiklash havolasi yaroqsiz'), 401)

            # Set the new password
            user.set_password(new_password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed(_('Parolni tiklash havolasi yaroqsiz'), 401)

