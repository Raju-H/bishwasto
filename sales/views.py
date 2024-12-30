from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.db.models import Q
from products.models import *
from .models import *
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class SalesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Sales
    template_name = 'sales/sales_list.html'
    context_object_name = 'sales'

    def test_func(self):
        return self.request.user.has_perm('sales.view_sales')


class SaleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Sales
    fields = ['customer', 'payment_method', 'sub_total', 'grand_total', 'amount_payed', 'amount_change', 'notes']
    template_name = 'sales/sales_form.html'
    success_url = reverse_lazy('sales_create')

    def test_func(self):
        return self.request.user.has_perm('sales.add_sales')
    
    def form_valid(self, form):
        # Save the form but do not commit yet
        self.object = form.save(commit=False)
        # Set the employee field to the current user
        self.object.employee = self.request.user
        
        # Retrieve sales items from session and associate with the sale
        sales_items = self.request.session.get('sales_items', [])
        
        # Now save the object to the database
        self.object.save()

        # Clear sales items from session after saving
        del self.request.session['sales_items']

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Sales'
        context['submit_text'] = 'Complete'
        
        # Retrieve sales items from session for display in the template
        context['sales_items'] = self.request.session.get('sales_items', [])
        
        return context




def search_products(request):
    query = request.POST.get('q')
    if query:
        products = ShopProduct.objects.filter(Q(product__name__icontains=query) | Q(product__slug__icontains=query)).select_related().filter(is_active=True)[:10]
    else:
        products = []

    context = {'products': products}
    return render(request, 'sales/search_results.html', context)






def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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
            is_active=True
        )[:10]

        data = [product.to_json() for product in products]
        return JsonResponse(data, safe=False)

    except Exception as e:
        logger.error(f"Error fetching shop products: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
