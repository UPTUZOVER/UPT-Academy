from base.models import Teacher, Pupil, Parent, Administrator
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()
CustomUser: object = get_user_model()
from rest_framework import serializers



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type']

class PupilSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Pupil
        fields = [
            'id', 'user',  'first_name', 'last_name',
            'address', 'phone_number', 'age', 'status', 'gmail',
            'image', 'created_on', 'updated_on'
        ]


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.create(**user_data)
        pupil = Pupil.objects.create(user=user, **validated_data)
        return pupil


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        instance.user.username = user_data.get('username', user.username)
        instance.user.email = user_data.get('email', user.email)
        instance.user.user_type = user_data.get('user_type', user.user_type)
        instance.user.save()

        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.age = validated_data.get('age', instance.age)
        instance.status = validated_data.get('status', instance.status)
        instance.gmail = validated_data.get('gmail', instance.gmail)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance





class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        user = None
        if '@' in username_or_email:
            user = authenticate(email=username_or_email, password=password)
        else:
            user = authenticate(username=username_or_email, password=password)

        if user is None:
            raise serializers.ValidationError(_('Invalid login credentials.'))

        attrs['user'] = user
        return attrs