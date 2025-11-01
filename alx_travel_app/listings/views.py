from rest_framework import viewsets
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    from .tasks import send_booking_confirmation_email

    def perform_create(self, serializer):
        booking = serializer.save()
        user_email = booking.user.email
        booking_details = f"Destination: {booking.destination}\nDate: {booking.date}\nPrice: {booking.price}"
        self.send_booking_confirmation_email.delay(user_email, booking_details)



import os
import time
import re
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Payment

CHAPA_URL = "https://api.chapa.co/v1/transaction/initialize"
VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"

# Simple email validation
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

class InitializePaymentView(APIView):
    def post(self, request):
        data = request.data
        chapa_secret_key = os.getenv("CHAPA_SECRET_KEY")
        if not chapa_secret_key:
            return Response({"error": "Chapa secret key not set"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        booking_ref = data.get("booking_reference")
        if not booking_ref:
            return Response({"error": "booking_reference is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate booking exists
        try:
            booking = Booking.objects.get(id=int(booking_ref))
        except (Booking.DoesNotExist, ValueError):
            return Response({"error": "Invalid booking reference"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Use booking user info for email and names
        email = (booking.user.email or "").strip()
        if not email:
            return Response({"error": "Valid email is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not is_valid_email(email):
            return Response({"error": "Invalid email format"},
                            status=status.HTTP_400_BAD_REQUEST)

        first_name = booking.user.first_name or data.get("first_name", "")
        last_name = booking.user.last_name or data.get("last_name", "")

        # Amount
        try:
            amount = float(data.get("amount") or booking.listing.price_per_night)
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        # Unique transaction reference
        tx_ref = f"booking-{booking.id}-{int(time.time())}"

        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": "http://127.0.0.1:8000/api/verify-payment/"
        }

        headers = {
            "Authorization": f"Bearer {chapa_secret_key}",
            "Content-Type": "application/json"
        }

        # Call Chapa API
        try:
            resp = requests.post(CHAPA_URL, json=payload, headers=headers)
            res_data = resp.json()
        except Exception as e:
            return Response({"error": "Failed to call Chapa API", "details": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        # Save payment if successful
        if resp.status_code in (200, 201) and res_data.get("status") == "success" and res_data.get("data"):
            Payment.objects.create(
                booking_reference=str(booking.id),
                amount=amount,
                transaction_id=tx_ref,
                status="Pending"
            )
            return Response(res_data, status=status.HTTP_200_OK)

        # Return failure response
        return Response({"error": "Failed to initialize payment", "details": res_data},
                        status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    def get(self, request, tx_ref):
        chapa_secret_key = os.getenv("CHAPA_SECRET_KEY")
        headers = {"Authorization": f"Bearer {chapa_secret_key}"}
        response = requests.get(f"{VERIFY_URL}{tx_ref}", headers=headers)
        res_data = response.json()

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
            if res_data.get("status") == "success" and res_data["data"]["status"] == "success":
                payment.status = "Completed"
            else:
                payment.status = "Failed"
            payment.save()
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(res_data)

