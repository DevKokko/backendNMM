
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from .models import User_Info
import secrets
from django.core.mail import send_mail
from django.template import loader, Template, Context

class UserSerializerWithToken(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    username = serializers.CharField(
            required=True,max_length=32,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    
    password = serializers.CharField(required=True,min_length=8,write_only=True)
    
    first_name =serializers.CharField(required=True,min_length=2)
    last_name =serializers.CharField(required=True,min_length=2)

    token = serializers.SerializerMethodField()
    
    def get_token(self, object):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(object)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        username = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        password = validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(
            username = username,
            first_name = first_name,
            last_name = last_name,
            password = password,
            email = email
        )
        user.save()
        verification_token = secrets.token_hex(16)
        user_info = User_Info(user = user, verification_token = verification_token)
        user_info.save()

        subject = "NMM - Please verify your email"
        message = "Please verify your email"
        toMails = [email]
        verification_link = "https://nmm.alexandros-kalogerakis.com/verify_account?token="+verification_token
        template = Template('''
                <!DOCTYPE html>
                <html>
                    <head>
                    </head>
                    <body>
                        <p>Hello {{ first_name }} {{ last_name }},</p>
                        <p>Please follow <a href="{{ verification_link }}">this link</a> to verify your account</p>
                    </body>
                </html>''')
        context = Context({"first_name": first_name, "last_name": last_name, "verification_link": verification_link})
        html_message = template.render(context)
        send_mail(subject, message, 'NMM Support <contact@alexandros-kalogerakis.com>', toMails, fail_silently=False, html_message=html_message)

        return user
    
    class Meta:
        model = User
        fields = ('token','id', 'username', 'email','password', 'first_name', 'last_name')


class UserUpdate(serializers.Serializer):
    old_password = serializers.CharField(required=True,min_length=8,write_only=True)
    new_password = serializers.CharField(required=True,min_length=8,write_only=True)
    new_password2 = serializers.CharField(required=True,min_length=8,write_only=True)
    first_name = serializers.CharField(required=True,min_length=2)
    last_name = serializers.CharField(required=True,min_length=2)


class CheckUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    username = serializers.CharField(
            max_length=32,required=False,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    class Meta:
        model = User
        fields = ('username', 'email',)


class GetIDUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','username', 'is_staff', 'is_verified_account')
    
    is_verified_account = serializers.BooleanField(source='user_info.is_verified_account')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'elo', 'is_verified_account')

    elo = serializers.IntegerField(source='user_info.elo') 
    is_verified_account = serializers.BooleanField(source='user_info.is_verified_account')


class AdminUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'elo', 'is_banned', 'is_verified_account', 'is_staff')

    elo = serializers.IntegerField(source='user_info.elo')
    is_verified_account = serializers.BooleanField(source='user_info.is_verified_account')
    is_banned = serializers.BooleanField(source='user_info.is_banned')
    is_staff = serializers.BooleanField(source='user_info.is_staff')