# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Python import

# Django import

# Contrib import
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from djstripe.settings import (
    subscriber_request_callback,
    CANCELLATION_AT_PERIOD_END,
)
from djstripe.models import Customer

# Project import
from .serializers import (
    SubscriptionSerializer,
    CreateSubscriptionSerializer,
)


class SubscriptionRestView(APIView):
    """
    A REST API for Stripes implementation in the backend
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return the users current subscription
        """
        try:
            customer = self.request.user.customer
            subscription = customer.current_subscription

            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)

        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        serializer = CreateSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                customer, created = Customer.get_or_create(
                    subscriber=subscriber_request_callback(self.request)
                )
                customer.update_card(serializer.data["stripe_token"])
                customer.subscribe(serializer.data["plan"])
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except InvalidRequestError:
                return Response(
                    "Something went wrong processing the payment.",
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, format=None):
        """
        Return the users current subscription
        """
        try:
            customer, created = Customer.get_or_create(
                subscriber=subscriber_request_callback(self.request)
            )
            customer.cancel_subscription(
                at_period_end=CANCELLATION_AT_PERIOD_END
            )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except:
            return Response(
                "Something went wrong cancelling the subscription.",
                status=status.HTTP_400_BAD_REQUEST
            )
