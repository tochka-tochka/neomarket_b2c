from django.contrib import admin, messages
from src.models.orders import Order, OrderItem, OrderStatus
from .models import Category, CategoryFilter, CategorySEOKeyword
from src.services.orders.admin_orders import fulfill_order

admin.site.register(Category)
admin.site.register(CategoryFilter)
admin.site.register(CategorySEOKeyword)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ["name", "unit_price", "quantity", "line_total"]
    readonly_fields = ["name", "unit_price", "quantity", "line_total"]
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ["id", "buyer", "status"]
    actions = ["mark_as_delivered"]

    def save_model(self, request, obj, form, change):
        is_status_changed_to_delivered = False

        if change:
            old_status = Order.objects.filter(pk=obj.pk).values_list('status', flat=True).first()
            if old_status != "DELIVERED" and obj.status == "DELIVERED":
                is_status_changed_to_delivered = True

        super().save_model(request, obj, form, change)

        if is_status_changed_to_delivered:
            try:
                fulfill_order(id=obj.id)
                self.message_user(request, "Заказ успешно доставлен и отправлен в B2B систему.")
            except Exception as e:
                self.message_user(
                    request, 
                    f"Статус изменен, но не удалось уведомить B2B сервис: {e}", 
                    level=messages.ERROR
                )

    @admin.action(description="Отметить выбранные заказы как доставленные (если заказ не отменен)")
    def mark_as_delivered(self, request, queryset):
        success_count = 0
        error_count = 0

        for order in queryset:
            if order.status != "DELIVERED" and order.status != "CANCELLED":
                order.status = "DELIVERED"
                order.save()
                
                try:
                    fulfill_order(id=order.id)
                    success_count += 1
                except Exception as e:
                    error_count += 1

        if success_count:
            self.message_user(request, f"Успешно обработано заказов: {success_count}.", messages.SUCCESS)
        if error_count:
            self.message_user(request, f"Ошибка отправки во внешний сервис для {error_count} заказов.", messages.ERROR)