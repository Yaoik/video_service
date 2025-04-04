from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class SocialLoginCallbackView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request: Request):
        refresh = RefreshToken.for_user(request.user)
        redirect_url = request.query_params.get('f')
        if redirect_url:
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            params = urlencode(tokens)
            if '?' in redirect_url:
                full_url = f"{redirect_url}&{params}"
            else:
                full_url = f"{redirect_url}?{params}"
            return redirect(full_url)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })