from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.files.storage import default_storage
from django.db.models import Q
from .models import *




class ShopCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Shop
    fields = ['name', 'address', 'phone_number', 'email', 'return_policy', 'website', 'shop_logo', 'employees', 'is_active']
    template_name = 'backend/shops/shop_form.html'
    success_url = reverse_lazy('myshop_list')

    def test_func(self):
        return self.request.user.has_perm('shops.add_shop')

    def form_valid(self, form):
        # Create the shop instance but don't save to DB yet
        self.object = form.save(commit=False)
        self.object.save()
        
        # Add the creator as an owner
        self.object.owner.add(self.request.user)
        
        # Handle M2M fields
        form.save_m2m()
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Shop'
        context['submit_text'] = 'Create Shop'
        return context








class ShopUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Shop
    fields = ['name', 'address', 'phone_number', 'email', 'return_policy', 'website', 'shop_logo', 'employees', 'is_active']
    template_name = 'backend/shops/shop_form.html'
    success_url = reverse_lazy('myshop_list')

    def test_func(self):
        shop = self.get_object()
        
        # Check if the user is trying to update an existing shop
        if self.kwargs.get('pk'):
            # Ensure the user is the owner of the shop and has permission to change it
            return self.request.user.has_perm('shops.change_shop')
        
        # If no pk is present, we do not allow access (or handle as needed)
        return False


    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You don't have permission to edit this shop.")
    
    def get_object(self, queryset=None):
        """Override to get the object for update."""
        if self.kwargs.get('pk'):
            return get_object_or_404(Shop, pk=self.kwargs['pk'])
        return None
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Shop: {self.object.name}'
        context['submit_text'] = 'Update Shop'
        return context

    @transaction.atomic
    def form_valid(self, form):
        instance = form.save(commit=False)
        old_instance = self.get_object()

        # Check if this is an update and if the shop logo is being changed
        if self.object and 'shop_logo' in form.changed_data:
            if old_instance.shop_logo != instance.shop_logo:
                # Delete the old image file if it exists
                if default_storage.exists(old_instance.shop_logo.path):
                    default_storage.delete(old_instance.shop_logo.path)

        return super().form_valid(form)




class MyShopsListView(LoginRequiredMixin, ListView):
    model = Shop
    template_name = 'backend/shops/my_shops.html'
    context_object_name = 'shops'
    paginate_by = 10

    def get_queryset(self):
        queryset = Shop.objects.filter(owner=self.request.user)
        
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search) |
                Q(owner__email__icontains=search) |
                Q(phone_number__icontains=search)
            )

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_shops = Shop.objects.filter(owner=self.request.user)
        context.update({
            'active_shops_count': user_shops.filter(is_active=True).count(),
            'total_employees': sum(shop.employees.count() for shop in user_shops),
            'search_query': self.request.GET.get('search', ''),
            'title': 'My Shops',
        })
        
        return context
    
    




class ShopListView(LoginRequiredMixin, ListView):
    model = Shop
    template_name = 'backend/shops/shop_list.html'
    context_object_name = 'shops'
    paginate_by = 10

    def get_queryset(self):
        queryset = Shop.objects.select_related().prefetch_related(
            'owner',
            'employees'
        ).distinct()
    
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search) |
                Q(owner__email__icontains=search) |
                Q(phone_number__icontains=search)
            )

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        # Filter by owner if not superuser
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(owner=self.request.user) |
                Q(employees=self.request.user)
            )

        # Sort by name, -name, created_at, -created_at
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == '-name':
            queryset = queryset.order_by('-name')
        elif sort_by == 'created_at':
            queryset = queryset.order_by('created_at')
        elif sort_by == '-created_at':
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter parameters to context
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'status_filter': self.request.GET.get('status', ''),
            'sort_by': self.request.GET.get('sort_by', ''),
            'title': 'Shops',
            'total_shops': self.get_queryset().count(),
            'active_shops': self.get_queryset().filter(is_active=True).count(),
            'inactive_shops': self.get_queryset().filter(is_active=False).count(),
        })

        return context
