from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from users.permissions import UserPermission
from .models import Korik
from .serializers import KorikModelSerializer

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class KorikModelViewSet(ModelViewSet):
    queryset = Korik.objects.all()
    serializer_class = KorikModelSerializer

    def create(self, request, *args, **kwargs):
        self.permission_classes = (UserPermission, )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.permission_classes = (UserPermission, )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.permission_classes = (UserPermission, )
        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.permission_classes = (UserPermission, )
        return super().partial_update(request, *args, **kwargs)


class KorikPDFAPIView(APIView):
    permission_classes = [AllowAny]  # Agar authentication kerak bo‘lsa, moslashtiring

    def get(self, request, korik_id, *args, **kwargs):
        try:
            korik = Korik.objects.get(id=korik_id)
        except Korik.DoesNotExist:
            return Response({"error": "Ko‘rik topilmadi"}, status=404)

        # HTTP javob yaratish
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="korik_{korik_id}.pdf"'

        # PDF generatsiya qilish
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # **Sarlavha**
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "Ko‘rik ma’lumotlari")

        # **Bemor haqida ma’lumot**
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 100, f"Bemor: {korik.bemor.bemor.ism} {korik.bemor.bemor.familiya}")
        p.drawString(50, height - 120, f"Tug‘ilgan sana: {korik.bemor.bemor.tugilgan_sana}")

        # **Ko‘rik ma’lumotlari**
        p.drawString(50, height - 160, f"Ko‘rik sanasi: {korik.korik_otkazilgan_sana}")
        p.drawString(50, height - 180, f"Murojaat turi: {korik.murojat_turi}")
        p.drawString(50, height - 200, f"Qon olingan sana: {korik.qon_olingan_sana}")
        p.drawString(50, height - 220, f"Qon analiz qilingan sana: {korik.qon_analiz_qilingan_sana}")
        p.drawString(50, height - 240, f"Reagent ishlatildimi: {'Ha' if korik.reagent_ishlatildi else 'Yo‘q'}")

        p.setFont("Helvetica-Bold", 12)
        # p.drawString(50, height - 260, "Qo'shimcha malumotlar")
        p.drawString(50, height - 280, f"Qo'shimcha malumot:")
        p.drawString(50, height - 300, f" {korik.description}")
        # **Tavsiya qilingan dorilar**
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 340, "Tavsiya qilingan dorilar:")
        p.setFont("Helvetica", 12)

        y_position = height - 360
        for idx, dori in enumerate(korik.korik_dorilari.all(), start=1):
            p.drawString(50, y_position, f"{idx}. {dori.dori} - {dori.dozasi} mg")
            y_position -= 20
        # **PDFni yopish va javobni qaytarish**
        # y_position -= 160

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - y_position, "Analiz Natijalari:")
        p.setFont("Helvetica", 12)
        y_position = y_position + 20
        for idx, obj in enumerate(korik.analiz_natijalari.all(), start=1):
            p.drawString(50, height - y_position, f"gemoglabin {obj.gemoglabin}")
            p.drawString(50, height - y_position - 20, f"trombosit {obj.trombosit}")
            p.drawString(50, height - y_position - 40, f"leykosit {obj.leykosit}")
            p.drawString(50, height - y_position - 60, f"eritrosit {obj.eritrosit}")
            p.drawString(50, height - y_position - 80, f"limfosit {obj.limfosit}")
            y_position -= 120

        p.showPage()
        p.save()
        return response
