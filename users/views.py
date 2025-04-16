from tokenize import TokenError

from drf_yasg.openapi import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView
from rest_framework import permissions, status
from .models import CustomUser
from .serializers import SignUpSerializer, LoginSerializer, LogoutSerializer


class CreateUserView(CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = serializer.validated_data['refresh']  # validated_data dan olish kerak!
            token = RefreshToken(refresh)
            token.blacklist()

            data = {
                "success": True,
                "message": "Successfully logged out",
                "data": serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response(
                {
                    "success": False,
                    "message": "Token is invalid or expired",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
