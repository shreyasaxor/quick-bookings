from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hotel, HotelSyncLog
from .serializers import (
    HotelListSerializer,
    HotelDetailSerializer,
    HotelSearchRequestSerializer,
)
from .services.hotel_sync_service import HotelSyncService


class HotelPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HotelViewSet(viewsets.ModelViewSet):
    """ViewSet for Hotel operations"""
    queryset = Hotel.objects.filter(is_active=True).prefetch_related('images', 'amenities')
    permission_classes = [AllowAny]
    pagination_class = HotelPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'country_code', 'destination_code', 'city']
    search_fields = ['name', 'address', 'city', 'hotelbeds_code']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return HotelDetailSerializer
        return HotelListSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def search(self, request):
        """Search and sync hotels from Hotelbeds API"""
        serializer = HotelSearchRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            sync_service = HotelSyncService()
            result = sync_service.sync_hotels(
                destination_code=serializer.validated_data['destination'],
                check_in=serializer.validated_data.get('check_in'),
                check_out=serializer.validated_data.get('check_out'),
                rooms=serializer.validated_data.get('rooms', 1),
                adults=serializer.validated_data.get('adults', 1),
                children=serializer.validated_data.get('children', 0),
                limit=serializer.validated_data.get('limit', 100)
            )

            # Fetch newly synced hotels
            destination = serializer.validated_data['destination']
            hotels = Hotel.objects.filter(
                destination_code=destination,
                is_active=True
            ).prefetch_related('images', 'amenities')[:serializer.validated_data.get('limit', 100)]

            return Response({
                'sync_result': result,
                'hotels': HotelListSerializer(hotels, many=True).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def by_destination(self, request):
        """Get hotels by destination"""
        destination = request.query_params.get('destination')
        
        if not destination:
            return Response(
                {'error': 'destination parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        hotels = self.get_queryset().filter(destination_code=destination)
        page = self.paginate_queryset(hotels)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(hotels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def sync_status(self, request):
        """Get the status of the last hotel sync"""
        sync_service = HotelSyncService()
        status_data = sync_service.get_last_sync_status()
        return Response(status_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def sync_history(self, request):
        """Get sync history"""
        limit = request.query_params.get('limit', 10)
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 10

        logs = HotelSyncLog.objects.all()[:limit]
        
        data = [
            {
                'id': log.id,
                'sync_date': log.sync_date,
                'status': log.status,
                'total_processed': log.total_hotels_processed,
                'created': log.hotels_created,
                'updated': log.hotels_updated,
                'failed': log.hotels_failed,
                'duration': log.duration_seconds,
                'error_message': log.error_message,
            }
            for log in logs
        ]
        
        return Response(data, status=status.HTTP_200_OK)
