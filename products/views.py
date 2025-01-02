from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from .models import *
from django.db.models import Q
from django.db import transaction
from django.core.files.storage import default_storage
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
import qrcode
from PIL import Image, ImageDraw, ImageFont 




class ProductCategoryCreateUpdateView(LoginRequiredMixin, UserPassesTestMixin, CreateView, UpdateView):
    model = ProductCategory
    fields = ['name', 'description', 'is_active']
    template_name = 'backend/products/category/product_category_form.html'
    success_url = reverse_lazy('product_category_list')

    def test_func(self):
        # Check if user has permission to create/update
        if self.kwargs.get('pk'):
            return self.request.user.has_perm('products.change_productcategory')
        return self.request.user.has_perm('products.add_productcategory')

    def form_valid(self, form):
        # Save the form but do not commit yet
        self.object = form.save(commit=False)
        # Set the created_by field to the current user
        self.object.created_by = self.request.user
        # Now save the object to the database
        self.object.save()
        
        # Call the superclass's form_valid method to handle any additional logic
        return super().form_valid(form)

    def get_object(self, queryset=None):
        """Override to get the object for update."""
        if self.kwargs.get('pk'):
            return get_object_or_404(ProductCategory, pk=self.kwargs['pk'])
        return None
        
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        is_update = bool(self.kwargs.get('pk'))
        context.update({
            'is_update': is_update,
            'title': 'Update Category' if is_update else 'Create Category'
        })
        return context


class ProductCategoryListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = 'backend/products/category/product_category_list.html'
    context_object_name = 'product_categories'
    paginate_by = 10

    def get_queryset(self):
        queryset = ProductCategory.objects.all()
    
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                )

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)


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
            'title': 'Product Categories',
        })

        return context



class ProductSubCategoryCreateUpdateView(LoginRequiredMixin, UserPassesTestMixin, CreateView, UpdateView):
    model = ProductSubCategory
    fields = ['category', 'name', 'description', 'category', 'is_active']
    template_name = 'backend/products/sub/product_sub_category_form.html'
    success_url = reverse_lazy('product_sub_category_list')

    def test_func(self):
        # Check if user has permission to create/update
        if self.kwargs.get('pk'):
            return self.request.user.has_perm('products.change_productsubcategory')
        return self.request.user.has_perm('products.add_productsubcategory')

    def form_valid(self, form):
        # Save the form but do not commit yet
        self.object = form.save(commit=False)
        # Set the created_by field to the current user
        self.object.created_by = self.request.user
        # Now save the object to the database
        self.object.save()

        # Call the superclass's form_valid method to handle any additional logic
        return super().form_valid(form)

    def get_object(self, queryset=None):
        """Override to get the object for update."""
        if self.kwargs.get('pk'):
            return get_object_or_404(ProductSubCategory, pk=self.kwargs['pk'])
        return None

    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        is_update = bool(self.kwargs.get('pk'))
        context.update({
            'is_update': is_update,
            'title': 'Update Sub Category' if is_update else 'Create Sub Category'
        })
        return context
    


class ProductSubCategoryListView(LoginRequiredMixin, ListView):
    model = ProductSubCategory
    template_name = 'backend/products/sub/product_sub_category_list.html'
    context_object_name = 'product_sub_categories'
    paginate_by = 10

    def get_queryset(self):
        queryset = ProductSubCategory.objects.all()
    
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                )

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

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
            'title': 'Product Sub Categories',
        })

        return context
    



class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['category', 'sub_category', 'name', 'description', 'model', 'sku', 'isbn', 'variant', 'is_expirable', 'expiry_date', 'weight_unit', 'weight', 'length_unit', 'length', 'width', 'height', 'avatar', 'is_active']
    template_name = 'backend/products/product_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.has_perm('products.add_product')
        

    def form_valid(self, form):
        # Save the form but do not commit yet
        self.object = form.save(commit=False)
        # Set the created_by field to the current user
        self.object.created_by = self.request.user
        # Now save the object to the database
        self.object.save()

        # Call the superclass's form_valid method to handle any additional logic
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Product'
        context['submit_text'] = 'Create Product'
        return context

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['category', 'sub_category', 'name', 'description', 'model', 'sku', 'isbn', 'variant', 'is_expirable', 'expiry_date', 'weight_unit', 'weight', 'length_unit', 'length', 'width', 'height', 'avatar', 'is_active']
    template_name = 'backend/products/product_form.html'
    success_url = reverse_lazy('product_list')

    def test_func(self):
        return self.request.user.has_perm('products.change_product')
    
    def get_object(self, queryset=None):
        """Override to get the object for update."""
        if self.kwargs.get('pk'):
            return get_object_or_404(Product, pk=self.kwargs['pk'])
        return None
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit Product: {self.object.name}"
        context['submit_text'] = 'Update Product'
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        instance = form.save(commit=False)
        old_instance = self.get_object()

        # Check if this is an update and if the shop logo is being changed
        if self.object and 'avatar' in form.changed_data:
            if old_instance.avatar != instance.avatar:
                # Delete the old image file if it exists
                if default_storage.exists(old_instance.avatar.path):
                    default_storage.delete(old_instance.avatar.path)

        return super().form_valid(form)



class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'backend/products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.all()
    
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search) | Q(isbn__icontains=search)
                )

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

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
            'title': 'Products',
        })

        return context






class ShopProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ShopProduct
    fields = [
        'shop', 'supplier', 'product', 'buying_price', 'wholesale_price', 'retail_price',
        'stock_quantity', 'receivings_stock', 'sort_order',
        'stock_warning_threshold', 'default_tax_rate', 'is_active'
    ]
    template_name = 'backend/products/shop_product/shop_product_form.html'
    success_url = reverse_lazy('shop_product_list')

    def test_func(self):
        return self.request.user.has_perm('products.add_shopproduct')

    def form_valid(self, form):
        try:
            # Save the form but do not commit yet
            self.object = form.save(commit=False)

            # Check if the product is valid before accessing its slug
            if self.object.product and hasattr(self.object.product, 'slug') and self.object.product.slug:
                qr_data = str(self.object.product.slug)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Convert to PIL Image for drawing text
                img = img.convert("RGB")
                draw = ImageDraw.Draw(img)

                # Define font and size (you may need to adjust the path to a valid font file)
                font_size = 20
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)  # Use a TrueType font
                except IOError:
                    font = ImageFont.load_default()  # Fallback to default font if arial.ttf is not available

                # Prepare text to draw (retail price)
                retail_price_text = f"Retail Price: {self.object.retail_price}TK"
                
                # Calculate text bounding box and position
                bbox = draw.textbbox((0, 0), retail_price_text, font=font)
                text_width = bbox[2] - bbox[0]  # width of the text box
                text_height = bbox[3] - bbox[1]  # height of the text box
                
                width, height = img.size
                text_x = (width - text_width) / 2  # Center horizontally
                text_y = height - text_height - 10  # Position above the bottom edge

                # Draw text on the image
                draw.text((text_x, text_y), retail_price_text, fill="black", font=font)

                # Save QR code image to a BytesIO buffer
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                qr_code_data = buffer.getvalue()
                buffer.close()
                
                self.object.qrcode.save(f"{self.object.product.slug}.png", ContentFile(qr_code_data))

            # Set created_by field to current user
            self.object.created_by = self.request.user
            self.object.save()

            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Error saving product: {str(e)}")
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Product to Shop'
        context['submit_text'] = 'Add Product to Shop'
        return context





class ShopProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ShopProduct
    fields = [
        'shop', 'supplier', 'product', 'buying_price', 'wholesale_price', 'retail_price',
        'stock_quantity', 'receivings_stock', 'sort_order',
        'stock_warning_threshold', 'default_tax_rate', 'is_active'
    ]
    template_name = 'backend/products/shop_product/shop_product_form.html'
    success_url = reverse_lazy('shop_product_list')

    def test_func(self):
        return self.request.user.has_perm('products.change_shopproduct')

    def get_object(self, queryset=None):
        """Override to get the object for update."""
        if self.kwargs.get('pk'):
            return get_object_or_404(ShopProduct, pk=self.kwargs['pk'])
        return None

    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit Shop Product: {self.object.product.name}"
        context['submit_text'] = 'Update Shop Product'
        return context
    






class ShopProductListView(LoginRequiredMixin, ListView):
    model = ShopProduct
    template_name = 'backend/products/shop_product/shop_product_list.html'
    context_object_name = 'shopproducts'
    paginate_by = 10

    def get_queryset(self):
        queryset = ShopProduct.objects.all().order_by('-created_at')
    
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) | Q(product__slug__icontains=search) | Q(product__isbn__icontains=search)
                )

        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        # Sort by name, -name, created_at, -created_at
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'name':
            queryset = queryset.order_by('product__name')
        elif sort_by == '-name':
            queryset = queryset.order_by('-product__name')
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
            'title': 'Shop Products',
        })

        return context

