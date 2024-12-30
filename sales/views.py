from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, ListView
from products.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging
from customers.models import *
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import SalesForm 
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
    form = SalesForm()

    if request.method == 'POST':
        if is_ajax(request=request):
            data = json.load(request)

            sale_attributes = {
                'customer': data.get('customer'),
                'quantity': data.get('quantity'),
                'discount': data.get('discount'),
                'payment_method': data.get('payment_method'),
                'payment_status': data.get('payment_status'),
                'note': data.get('note'),
                'created_by': request.user
            }

            form = SalesForm(data)
            
            if form.is_valid():
                try:
                    sale = form.save(commit=False)
                    sale.created_by = request.user
                    sale.save()

                    messages.success(request, "Sale created successfully!")
                    return JsonResponse({'success': True, 'invoice_number': sale.invoice_number})
                except Exception as e:
                    messages.error(request, str(e))
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
            else:
                # Return validation errors as JSON response
                errors = {field: form.errors[field].tolist() for field in form.errors}
                return JsonResponse({'success': False, 'errors': errors}, status=400)

    context = {
        'title': 'Create New Sales',
        'submit_text': 'Complete',
        'form': form,
    }

    return render(request, 'sales/sales_form.html', context)











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


