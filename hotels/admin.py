from django.contrib import admin
from .models import (
    Hotel,
    HotelImage,
    HotelAmenity,
    HotelAmenities,
    HotelFacility,
    HotelRating,
    HotelSyncLog
)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'hotelbeds_code',
        'category',
        'city',
        'country_code',
        'is_active',
        'updated_at'
    ]
    list_filter = [
        'category',
        'country_code',
        'city',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'name',
        'hotelbeds_code',
        'city',
        'destination_code'
    ]
    readonly_fields = [
        'hotelbeds_code',
        'created_at',
        'updated_at',
        'last_synced'
    ]


@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'image_url', 'display_order']
    list_filter = ['hotel']
    search_fields = ['hotel__name']


@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(HotelAmenities)
class HotelAmenitiesAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'amenity']
    list_filter = ['amenity']
    search_fields = ['hotel__name', 'amenity__name']


@admin.register(HotelFacility)
class HotelFacilityAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'facility_type', 'name', 'is_available']
    list_filter = ['facility_type', 'is_available']
    search_fields = ['hotel__name', 'name']


@admin.register(HotelRating)
class HotelRatingAdmin(admin.ModelAdmin):
    list_display = [
        'hotel',
        'average_rating',
        'total_reviews',
        'cleanliness',
        'comfort',
        'location',
        'service'
    ]
    readonly_fields = ['updated_at']
    search_fields = ['hotel__name']


@admin.register(HotelSyncLog)
class HotelSyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'sync_date',
        'status',
        'total_hotels_processed',
        'hotels_created',
        'hotels_updated',
        'hotels_failed',
        'duration_seconds'
    ]
    list_filter = ['status', 'sync_date']
    readonly_fields = [
        'sync_date',
        'total_hotels_processed',
        'hotels_created',
        'hotels_updated',
        'hotels_failed',
        'duration_seconds'
    ]
    ordering = ['-sync_date']
