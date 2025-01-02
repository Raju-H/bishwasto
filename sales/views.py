from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from products.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import logging
from customers.models import *
import json



logger = logging.getLogger(__name__)


class SalesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Sales
    template_name = 'sales/sales_list.html'
    context_object_name = 'sales'

    def test_func(self):
        return self.request.user.has_perm('sales.view_sales')



def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required
def sales_create_view(request):
    if request.method == 'POST':
        if is_ajax(request=request):
            data = json.loads(request.body)

            # Fetch customer instance based on provided ID
            customer_id = data.get('customer')
            customer = get_object_or_404(Customer, id=customer_id)

            # Prepare sale data
            sale_data = {
                'customer': customer,
                'employee': request.user,
                'payment_method': data.get('payment_method'),
                'sub_total': data.get('sub_total'),
                'grand_total': data.get('grand_total'),
                'amount_payed': data.get('amount_payed'),
                'amount_change': data.get('amount_change'),
                'notes': data.get('notes'),
            }

            try:
                sale = Sales.objects.create(**sale_data)

                # Extract and validate sale items data
                sale_items_data = data.get('items', [])
                formatted_items = []

                for item in sale_items_data:
                    product_id = item.get('product_id')

                    # Fetch the ShopProduct instance using the product_id
                    product = get_object_or_404(ShopProduct, id=product_id)

                    formatted_item = {
                        'sales': sale,
                        'product': product,
                        'quantity': item.get('quantity'),
                        'sale_price': item.get('retail_price'),
                        'discount_in_percentage': item.get('discount_percentage'),
                        'profit_in_percentage': item.get('profit_percentage'),
                        'total_price': item.get('total_price')
                    }
                    formatted_items.append(SalesItems(**formatted_item))

                    # Use bulk_create for efficiency
                    SalesItems.objects.bulk_create(formatted_items)
                return JsonResponse({'success': True, 'message': 'Sale created successfully!'}, status=201)

            except Exception as e:
                logger.error(f"Error creating sale: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'sales/sales_form.html', {
        'customers': [c.to_select2() for c in Customer.objects.all()],
        'title': 'Create New Sale',
        'submit_text': 'Complete',
    })











@login_required
def get_shops_product_ajax_view(request):
    if not is_ajax(request):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    term = request.POST.get('term', '').strip()
    
    if not term:
        return JsonResponse({'error': 'Search term cannot be empty'}, status=400)

    try:
        products = ShopProduct.objects.filter(
            product__name__icontains=term,
            product__slug__icontains=term,
            is_active=True
        )[:10]

        data = [product.to_json() for product in products]
        return JsonResponse(data, safe=False)

    except Exception as e:
        logger.error(f"Error fetching shop products: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


