from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from .models import *






class SubscriptionPlanCreateUpdateView(LoginRequiredMixin, UserPassesTestMixin, CreateView, UpdateView):
    model = SubscriptionPlan
    fields = ['name', 'description', 'price', 'duration_months', 'is_active']
    template_name = 'backend/subscriptions/subscription_form.html'
    success_url = reverse_lazy('subscription_list')

    def test_func(self):
        # Check if user has permission to create/update
        if self.kwargs.get('pk'):
            return self.request.user.has_perm('subscriptions.change_subscriptionplan')
        return self.request.user.has_perm('subscriptions.add_subscriptionplan')

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
            return get_object_or_404(SubscriptionPlan, pk=self.kwargs['pk'])
        return None
        
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        is_update = bool(self.kwargs.get('pk'))
        context.update({
            'is_update': is_update,
            'title': 'Update Subscription' if is_update else 'Create Subscription'
        })
        return context




class SubscriptionPlanListView(LoginRequiredMixin, ListView):
    model = SubscriptionPlan
    template_name = 'backend/subscriptions/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 10
    ordering = ['-created_at']

