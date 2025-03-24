from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from shifokor.models import Shifokorlar, ShifokorQoshish
from .serializers import ShifokorModelSerializer, ShifokorListSerializer, ShifokorDetailUpdateModelSerializer, \
    ArxivShifokorModelSerializer
from shifokor.serializers import ShifokorQoshishModelSerializer
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny

import pandas as pd
from django.http import HttpResponse
from rest_framework.views import APIView

class ShifokorModelViewSet(ModelViewSet):
    queryset = Shifokorlar.objects.all()
    serializer_class = ShifokorModelSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = ShifokorListSerializer
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = ShifokorDetailUpdateModelSerializer
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ShifokorDetailUpdateModelSerializer
        return super().retrieve(request, *args, **kwargs)


class Shifokor_qoshish(CreateAPIView):
    queryset = ShifokorQoshish
    serializer_class = ShifokorQoshishModelSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            shifokor = self.queryset.objects.get(jshshir=request.data.get('jshshir'))
            return Response(
            {
                    "shifokor": {
                        "jshshir": shifokor.jshshir,
                        "ism": shifokor.ismi,
                        "familiya": shifokor.familya,
                        "tugilgan_sana": shifokor.tugilgan_sana,
                        "jinsi": shifokor.jinsi,
                    }
                },
                status=HTTP_200_OK
            )

        return Response(
            {
                "message": "Xatolik yuz berdi!",
                "errors": serializer.errors
            },
            status=HTTP_400_BAD_REQUEST
        )


class ArxivShifokorlar(ListAPIView):
    queryset = Shifokorlar.objects.all()
    serializer_class = ArxivShifokorModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(arxivga_olingan_sana__isnull = False)
        return qs

class ShifokorlarExcelDownloadAPIView(APIView):
    """Shifokorlar ro‘yxatini Excel formatida yuklab beradigan API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        shifokorlar = Shifokorlar.objects.select_related('shifokor')

        # Ma'lumotlarni JSON formatga o‘tkazamiz
        data = []
        for shifokor in shifokorlar:
            data.append({
                "Ism": shifokor.shifokor.ismi,
                "Familya": shifokor.shifokor.familya,
                "Otasining ismi": shifokor.shifokor.otasining_ismi,
                "Tug‘ilgan sana": shifokor.shifokor.tugilgan_sana.strftime('%Y-%m-%d') if shifokor.shifokor.tugilgan_sana else '',
                "Lavozimi": shifokor.lavozimi,
                "Mutaxassislik toifasi": shifokor.mutaxasislik_toifasi,
                "Telefon raqami": shifokor.telefon_raqami
            })

        # Pandas DataFrame yaratish
        df = pd.DataFrame(data)

        # Excel fayl yaratish
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="shifokorlar.xlsx"'

        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Shifokorlar")

        return response




