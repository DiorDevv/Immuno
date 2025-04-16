import logging
from datetime import date
import openpyxl
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.db import transaction
from rest_framework.decorators import action

from shared.cumtom_pagination import CustomPagination
from .filters import BemorFilter

logger = logging.getLogger(__name__)
from .models import BemorQoshish, Manzil, OperatsiyaBolganJoy, Bemor, Viloyat
from rest_framework.permissions import AllowAny
from .permissions import BemorPermission
from .serializers import BemorQoshishSerializer, ManzilSerializer, OperatsiyaBolganJoySerializer, \
    BemorSerializer, ViloyatSerializer
from rest_framework import permissions
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from openpyxl.styles import Alignment
from django.db.models import Count, F, Value
from django.views import View
from django.db.models.functions import Coalesce

from rest_framework.views import APIView
from django.http import HttpResponse
from .utils import generate_bemor_pdf


class BemorQoshishCreateView(CreateAPIView):
    queryset = BemorQoshish.objects.all()
    serializer_class = BemorQoshishSerializer
    permission_classes = [BemorPermission, ]
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            bemor_data = serializer.validated_data

            bemor, created = BemorQoshish.objects.get_or_create(
                JSHSHIR=bemor_data["JSHSHIR"],
                defaults=bemor_data
            )

            return Response(
                {
                    "message": "Bemor muvaffaqiyatli qo‘shildi!" if created else "Bemor allaqachon mavjud!",
                    "data": {
                        'id': bemor.id,
                        "JSHSHIR": bemor.JSHSHIR,
                        "ism": bemor.ism,
                        "familiya": bemor.familiya,
                        "tugilgan_sana": bemor.tugilgan_sana,
                        "jinsi": bemor.jinsi,
                    }
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Xatolik yuz berdi!",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ManzilViewSet(viewsets.ModelViewSet):
    queryset = Manzil.objects.all()
    serializer_class = ManzilSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Faqat kirgan user POST, PUT, DELETE qila oladi
    pagination_class = CustomPagination


class ViloyatViewSet(viewsets.ModelViewSet):
    queryset = Viloyat.objects.all()
    serializer_class = ViloyatSerializer  # TO‘G‘RI: serializer_class bo‘lishi kerak
    permission_classes = []
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):  # Swagger uchun tekshiruv
            return self.serializer_class
        if self.action == 'list':
            return ViloyatSerializer
        return super().get_serializer_class()


class OperatsiyaBolganJoyViewSet(viewsets.ModelViewSet):
    queryset = OperatsiyaBolganJoy.objects.all()
    serializer_class = OperatsiyaBolganJoySerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        # Qo‘shimcha tekshiruv: operatsiya sanasi tugash sanasidan oldin bo‘lishi kerak
        transplantatsiya_sana = serializer.validated_data.get('transplantatsiya_sana')
        operatsiya_oxirlangan_sana = serializer.validated_data.get('operatsiya_oxirlangan_sana')

        if transplantatsiya_sana > operatsiya_oxirlangan_sana:
            raise serializers.ValidationError(
                "Transplantatsiya sanasi operatsiya tugash sanasidan oldin bo‘lishi kerak!")

        serializer.save()


class BemorViewSet(viewsets.ModelViewSet):
    queryset = Bemor.objects.all().order_by('-created_at')
    serializer_class = BemorSerializer
    permission_classes = [BemorPermission, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BemorFilter
    search_fields = ['bemor__ism', 'bemor__familiya']
    ordering_fields = ['bemor__ism', 'bemor__id']
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        try:
            bemor_id = request.data.get("bemor")

            if not bemor_id:
                raise ValidationError({"error": "Bemor ID kiritilishi shart!"})

            # Bemor mavjudligini tekshirish
            if not BemorQoshish.objects.filter(id=bemor_id).exists():
                return Response(
                    {"error": "Bunday bemor mavjud emas!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Agar bemor allaqachon ro‘yxatda bo‘lsa, qaytaramiz
            existing_bemor = Bemor.objects.filter(bemor=bemor_id, manzil=request.data.get("manzil")).first()
            if existing_bemor:
                return Response(
                    {
                        "message": "Bu bemor allaqachon ro‘yxatda bor!",
                        "bemor": BemorSerializer(existing_bemor).data
                    },
                    status=status.HTTP_200_OK
                )

            return super().create(request, *args, **kwargs)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Server xatosi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def arxivlanganlar(self, request):
        # Faqat arxivlangan bemorlar
        bemorlar = Bemor.objects.filter(arxivlangan=False).order_by('-created_at')
        page = self.paginate_queryset(bemorlar)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(bemorlar, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def arxivlanmaganlar(self, request):
        # Faqat arxivlanmagan bemorlar
        bemorlar = Bemor.objects.filter(arxivlangan=True).order_by('-created_at')
        page = self.paginate_queryset(bemorlar)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(bemorlar, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def arxivlash(self, request, pk=None):
        # Bemorni arxivlash
        bemor = self.get_object()
        bemor.arxivlangan = False
        bemor.arxiv_sababi = request.data.get('sabab', 'Sabab ko‘rsatilmagan')
        bemor.save()
        return Response({'status': 'Bemor muvaffaqiyatli arxivlandi!'})

    @action(detail=True, methods=['post'])
    def arxivdan_chiqarish(self, request, pk=None):
        # Bemorni arxivdan chiqarish
        bemor = self.get_object()
        bemor.arxivlangan = True
        bemor.arxiv_sababi = request.data.get('sabab', 'Sabab ko‘rsatilmagan')
        bemor.save()
        return Response({'status': 'Bemor arxivdan chiqarildi!'})


class ExportBemorExcelView(View):

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Bemorlar"

        headers = [
            "JSHSHIR", "Ism", "Familiya", "Tug‘ilgan sana", "Yosh", "Jins", "Manzil",
            "Bemor holati", "Operatsiya joyi", "Qo‘shimcha ma'lumotlar", "Arxivga olingan sana"
        ]
        ws.append(headers)

        # Ustunlar kengaytiradi
        for col_num, column_title in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=column_title).alignment = Alignment(horizontal="center")

        # values_list malumotni tez oladi
        bemorlar = Bemor.objects.values_list(
            "bemor__JSHSHIR", "bemor__ism", "bemor__familiya", "bemor__tugilgan_sana", "bemor__jinsi",
            "manzil__viloyat__nomi", "manzil__tuman__nomi", "manzil__mahalla", "manzil__kocha_nomi",
            "bemor_holati__holati", "operatsiya_bolgan_joy__operatsiya_bolgan_joy",
            "qoshimcha_malumotlar", "arxivga_olingan_sana"
        )

        today = date.today().year

        for bemor in bemorlar:
            jshshir, ism, familiya, tugilgan_sana, jinsi, viloyat, tuman, mahalla, kocha, holat, operatsiya_joyi, qoshimcha, arxiv_sana = bemor

            birth_date = tugilgan_sana.strftime("%d-%m-%Y") if tugilgan_sana else ""
            yosh = today - tugilgan_sana.year if tugilgan_sana else ""

            gender = "Erkak" if jinsi == "M" else "Ayol"

            address_parts = filter(None, [viloyat, tuman, mahalla, kocha])  # Bo‘sh joylarni olib tashlaydi
            address = ", ".join(address_parts)

            arxiv_sana = arxiv_sana.strftime("%d-%m-%Y") if arxiv_sana else ""

            ws.append([jshshir, ism, familiya, birth_date, yosh, gender, address, holat, operatsiya_joyi, qoshimcha,
                       arxiv_sana])

        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 2

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="bemorlar.xlsx"'
        wb.save(response)

        return response


from django.utils.dateparse import parse_date


class BemorHolatiStatistika(APIView):
    permission_classes = []
    pagination_class = CustomPagination

    def get(self, request):
        # URL'dan sana olish: ?sana=2023-01-01
        sana = request.query_params.get('sana')

        bemorlar = Bemor.objects.all()

        if sana:
            parsed_sana = parse_date(sana)
            if parsed_sana:
                bemorlar = bemorlar.filter(created_at__date=parsed_sana)

        # Holatlar bo‘yicha statistika
        statistikalar = (
            bemorlar
            .annotate(
                holati_nomi=Coalesce(F('bemor_holati__holati'), Value("Noma'lum"))
            )
            .values('holati_nomi')
            .annotate(soni=Count('id'))
            .order_by('-soni')
        )

        # Jami bemorlar soni
        jami_bemorlar_soni = bemorlar.count()

        return Response({
            "success": True,
            "data": list(statistikalar),
            "jami_bemorlar": jami_bemorlar_soni
        })


class BemorPDFDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        return generate_bemor_pdf(pk)
