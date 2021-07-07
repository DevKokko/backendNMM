from rest_framework import status

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from . import serializers as srs
from . import models as mds
from rest_framework_jwt.views import ObtainJSONWebToken
from django.contrib.auth.models import User


# class LeaderboardViews():
   
#     class NMM_Leaderboard(APIView):
#         permission_classes = (AllowAny,)

#         def post(self, request, format='json'):
#             emmelo = mds.NMM_ELO_Rating.objects.order_by('-score')

#             return Response({"success":False}, status=status.HTTP_200_OK)


class UserLogin(ObtainJSONWebToken, APIView):
   
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        """
        Endpoint for user sign in, using JWT 
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code in [400,401]:
            return Response({"success":False}, status=status.HTTP_200_OK)
        
        is_banned = (User.objects.get(username=request.data["username"])).user_info.is_banned
        if is_banned:
            return Response({"success": False, "isBanned": True}, status=status.HTTP_200_OK)

        return response


class UserCreate(APIView):

    permission_classes = (AllowAny,)
          
    def get(self, request): #checks for validity of email and username
        """
        Endpoint for email/username validity check in sign up
        """
        data={}
        for key in request.GET.keys():
            data.update({key:request.GET[key]})

        if len(data)==1:
            serializer = srs.CheckUserSerializer(data=data)
            if serializer.is_valid():
                return Response({"success":False}, status=status.HTTP_200_OK)
        return Response({"success":True}, status=status.HTTP_200_OK)

    def post(self, request, format='json'):#creates the user
        """
        Endpoint for user sign up. JWT is created
        """
        password1=request.data.pop('password1',None)

        errors={}
        if request.data["password"]!=password1:
            errors.update({'passwords':'Passwords do not match'}) 
        
        serializer = srs.UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
                    
            if not errors:
                user = serializer.save()

                if user:
                    response={'success':True}
                    response.update({"data":{"token":serializer.data['token']}})
                    response['data']['userId']=serializer.data['id']
                    response['data']['username']=serializer.data['username']
                    response['data']['isAdmin']=False
                    response['data']['isVerified']=False

                    return Response(response, status=status.HTTP_201_CREATED)

        for key in serializer.errors.keys():
            errors.update({key:serializer.errors[key][0]})

        response={'success':False}
        response.update({"data":{"message":errors}})

        return Response(response, status=status.HTTP_200_OK)


class ChangeUserInfo(generics.UpdateAPIView):
   
    serializer_class = srs.UserUpdate
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Endpoint for user's own info edit
        """
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            response = {
                "success": False,
                "message": serializer.errors
            }
            return Response(response, status=status.HTTP_200_OK)

        # Request data is valid
        # Check old password
        if not self.object.check_password(request.data["old_password"]):
            response = {
                "success": False,
                "message": "Wrong existing password"
            }
            return Response(response, status=status.HTTP_200_OK)

        if serializer.data.get("new_password") != serializer.data.get("new_password2"):
            response = {
                "success": False,
                "message": "New passwords do not match"
            }
            return Response(response, status=status.HTTP_200_OK)

        # set new info
        self.object.set_password(request.data['new_password'])
        self.object.first_name = serializer.data.get("first_name")
        self.object.last_name = serializer.data.get("last_name")
        self.object.save()

        response = {
            "success": True,
            "message": "User info updated successfully!"
        }

        return Response(response, status=status.HTTP_200_OK)


class GetUserInfo(generics.RetrieveAPIView):
    serializer_class = srs.UserSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """
        Endpoint for retrieving user's own info
        """
        return Response(self.get_serializer(self.get_object()).data, status=status.HTTP_200_OK)


class VerifyAccount(generics.UpdateAPIView):
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user.user_info

    def update(self, request, *args, **kwargs):
        """
        Endpoint for account verification
        """
        self.object = self.get_object()

        if self.object.is_verified_account:
            response = {
                "success": False,
                "message": "Account is already verified",
                "redirect": True
            }
            return Response(response, status=status.HTTP_200_OK)

        token = request.data.pop('token', None)
        if token is None:
            response = {
                "success": False,
                "message": "No verification token provided",
                "redirect": True
            }
            return Response(response, status=status.HTTP_200_OK)

        legit_token = self.object.verification_token
        if token != legit_token:
            response = {
                "success": False,
                "message": "Invalid verification token"
            }
            return Response(response, status=status.HTTP_200_OK)

        self.object.is_verified_account = True      
        self.object.save()
        response = {
            "success": True,
        }
        return Response(response, status=status.HTTP_200_OK)


class AdminUpdateUser(generics.UpdateAPIView):
    model = User
    serializer_class = srs.AdminUpdateUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Endpoint for user info edit by an admin
        """
        self.admin_user = self.get_object()

        if not self.admin_user.is_staff:
            response = {
                "success": False,
                "message": "User is not admin"
            }
            return Response(response, status=status.HTTP_200_OK)
        
        user_id = request.data.pop('id', None)
        if user_id is None:
            response = {
                "success": False,
                "message": "User id missing"
            }
            return Response(response, status=status.HTTP_200_OK)

        # Partial update of the data
        try:
            user_to_edit = User.objects.get(id=user_id)
        except:
            response = {
                "success": False,
                "message": "User id does not exist"
            }
            return Response(response, status=status.HTTP_200_OK)

        serializer = self.serializer_class(user_to_edit, data=request.data, partial=True)
        if not serializer.is_valid():
            response = {
                "success": False,
                "message": serializer.errors
            }
            return Response(response, status=status.HTTP_200_OK)
            
        user_to_edit.first_name = request.data.get('first_name')
        user_to_edit.last_name = request.data.get('last_name')
        user_to_edit.is_staff = request.data.get('is_staff')

        user_info = user_to_edit.user_info
        user_info.elo = request.data.get('elo')
        user_info.is_banned = request.data.get('is_banned')
        user_info.is_verified_account = request.data.get('is_verified_account')

        user_info.save()
        user_to_edit.save()
        response = {
            "success": True,
        }
        return Response(response, status=status.HTTP_200_OK)