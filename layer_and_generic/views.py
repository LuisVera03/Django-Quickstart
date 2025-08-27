"""Layer and Generic app views.

Provides:
1. Auth flows using FormView pattern (Login, Register, Logout)
2. Dashboard view aggregating counts (service abstraction)
3. Hierarchy of generic class-based CRUD views for Table1/Table2/Table3
4. Separation of functions: Views -> Services -> Repositories -> ORM

Key design choices:
- Base mixins centralize common context (URL names, table name) to remove duplication.
- Services wrap repository calls to allow future business logic injection (validation, caching).
- Repositories isolate ORM calls, enabling easier unit testing/mocking.
"""

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import LoginForm, RegisterForm, Table1Form, Table2Form, Table3Form
from rest.models import Table1, Table2, Table3

# Services
from .services import (
    try_login, register_user, perform_logout,
    get_table1_list, get_table1_detail, create_table1_service, update_table1_service, delete_table1_service,
    get_table2_list, get_table2_detail, create_table2_service, update_table2_service, delete_table2_service,
    get_table3_list, get_table3_detail, create_table3_service, update_table3_service, delete_table3_service,
    get_dashboard_data
)

#
## Base Mixins for DRY principle
#

class BaseTableMixin:
    """Common context + URL name helpers for CRUD views.

    Exposes consistent keys to templates so generic templates can be reused.
    """
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_name'] = self.get_table_name()
        context.update(self.get_url_names())
        return context
    
    def get_table_name(self):
        """Return model class name (override if custom label needed)."""
        return self.model.__name__
    
    def get_url_names(self):
        """Compute conventional URL names from model name.

        Subclasses may override (Table1 keeps legacy short names).
        """
        table_name = self.model.__name__.lower()
        return {
            'list_url': f'{table_name}_list',
            'detail_url': f'{table_name}_detail',
            'create_url': f'{table_name}_create',
            'update_url': f'{table_name}_update',
            'delete_url': f'{table_name}_delete',
        }

class BaseTableListView(LoginRequiredMixin, BaseTableMixin, ListView):
    """Base list view with enforced ordering to guarantee pagination stability."""
    template_name = 'Generic_templates/list.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        return self.get_service_list().order_by('id')
    
    def get_service_list(self):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_list")

class BaseTableDetailView(LoginRequiredMixin, BaseTableMixin, DetailView):
    """Base detail view retrieving object via service layer."""
    template_name = 'Generic_templates/detail.html'
    context_object_name = 'object'
    
    def get_object(self, queryset=None):
        obj = self.get_service_detail(self.kwargs['pk'])
        if not obj:
            raise Http404(f"{self.get_table_name()} record not found")
        return obj
    
    def get_service_detail(self, pk):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_detail")

class BaseTableCreateView(LoginRequiredMixin, BaseTableMixin, CreateView):
    """Base create view delegating persistence to service function."""
    template_name = 'Generic_templates/form.html'
    
    def form_valid(self, form):
        try:
            self.object = self.get_service_create(form.cleaned_data)
            messages.success(self.request, f'{self.get_table_name()} record created successfully!')
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f'Error creating record: {str(e)}')
            return self.form_invalid(form)
    
    def get_service_create(self, data):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_create")

class BaseTableUpdateView(LoginRequiredMixin, BaseTableMixin, UpdateView):
    """Base update view with optimistic error handling."""
    template_name = 'Generic_templates/form.html'
    
    def get_object(self, queryset=None):
        obj = self.get_service_detail(self.kwargs['pk'])
        if not obj:
            raise Http404(f"{self.get_table_name()} record not found")
        return obj
    
    def form_valid(self, form):
        try:
            self.object = self.get_service_update(self.get_object(), form.cleaned_data)
            messages.success(self.request, f'{self.get_table_name()} record updated successfully!')
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f'Error updating record: {str(e)}')
            return self.form_invalid(form)
    
    def get_service_detail(self, pk):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_detail")
    
    def get_service_update(self, instance, data):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_update")

class BaseTableDeleteView(LoginRequiredMixin, BaseTableMixin, DeleteView):
    """Base delete view with success/failure messaging."""
    template_name = 'Generic_templates/confirm_delete.html'
    context_object_name = 'object'
    
    def get_object(self, queryset=None):
        obj = self.get_service_detail(self.kwargs['pk'])
        if not obj:
            raise Http404(f"{self.get_table_name()} record not found")
        return obj
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success = self.get_service_delete(self.object)
        if success:
            messages.success(request, f'{self.get_table_name()} record deleted successfully!')
        else:
            messages.error(request, 'Error deleting record')
        return redirect(self.get_success_url())
    
    def get_service_detail(self, pk):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_detail")
    
    def get_service_delete(self, instance):
        """Override in subclasses to provide service method"""
        raise NotImplementedError("Subclasses must implement get_service_delete")

#
## Login / Register (Using Generic Views)
#

class LoginView(FormView):
    """User login (FormView) with redirect if already authenticated."""
    template_name = 'LAG/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home_layer_and_generic')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home_layer_and_generic')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        success = try_login(self.request, **form.cleaned_data)
        if success:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Incorrect username or password")
            return self.form_invalid(form)

class RegisterView(FormView):
    """User registration; delegates create to service layer for testability."""
    template_name = 'LAG/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login_layer_and_generic')
    
    def form_valid(self, form):
        user = register_user(**form.cleaned_data)
        if user:
            messages.success(self.request, "User created successfully")
            return super().form_valid(form)
        else:
            messages.error(self.request, "User already exists")
            return self.form_invalid(form)

class LogoutView(View):
    """Stateless logout endpoint (POST only)."""
    def post(self, request):
        perform_logout(request)
        return redirect('login_layer_and_generic')

@login_required
def home(request):
    """Dashboard summarizing total records across tables."""
    context = get_dashboard_data()
    return render(request, 'LAG/home.html', context)

#
## Table1 CRUD Views (Optimized Generic Views)
#

class Table1ListView(BaseTableListView):
    model = Table1
    
    def get_service_list(self):
        return get_table1_list()
    
    def get_url_names(self):
        # Table1 uses legacy URL names for backward compatibility
        return {
            'list_url': 'list',
            'detail_url': 'detail',
            'create_url': 'create',
            'update_url': 'update',
            'delete_url': 'delete',
        }

class Table1DetailView(BaseTableDetailView):
    model = Table1
    
    def get_service_detail(self, pk):
        return get_table1_detail(pk)
    
    def get_url_names(self):
        return {
            'list_url': 'list',
            'detail_url': 'detail',
            'create_url': 'create',
            'update_url': 'update',
            'delete_url': 'delete',
        }

class Table1CreateView(BaseTableCreateView):
    model = Table1
    form_class = Table1Form
    success_url = reverse_lazy('list')
    
    def get_service_create(self, data):
        return create_table1_service(data)
    
    def get_url_names(self):
        return {
            'list_url': 'list',
            'detail_url': 'detail',
            'create_url': 'create',
            'update_url': 'update',
            'delete_url': 'delete',
        }

class Table1UpdateView(BaseTableUpdateView):
    model = Table1
    form_class = Table1Form
    success_url = reverse_lazy('list')
    
    def get_service_detail(self, pk):
        return get_table1_detail(pk)
    
    def get_service_update(self, instance, data):
        return update_table1_service(instance, data)
    
    def get_url_names(self):
        return {
            'list_url': 'list',
            'detail_url': 'detail',
            'create_url': 'create',
            'update_url': 'update',
            'delete_url': 'delete',
        }

class Table1DeleteView(BaseTableDeleteView):
    model = Table1
    success_url = reverse_lazy('list')
    
    def get_service_detail(self, pk):
        return get_table1_detail(pk)
    
    def get_service_delete(self, instance):
        return delete_table1_service(instance)
    
    def get_url_names(self):
        return {
            'list_url': 'list',
            'detail_url': 'detail',
            'create_url': 'create',
            'update_url': 'update',
            'delete_url': 'delete',
        }

#
## Table2 CRUD Views (Optimized Generic Views)
#

class Table2ListView(BaseTableListView):
    model = Table2
    success_url = reverse_lazy('table2_list')
    
    def get_service_list(self):
        return get_table2_list()

class Table2DetailView(BaseTableDetailView):
    model = Table2
    
    def get_service_detail(self, pk):
        return get_table2_detail(pk)

class Table2CreateView(BaseTableCreateView):
    model = Table2
    form_class = Table2Form
    success_url = reverse_lazy('table2_list')
    
    def get_service_create(self, data):
        return create_table2_service(data)

class Table2UpdateView(BaseTableUpdateView):
    model = Table2
    form_class = Table2Form
    success_url = reverse_lazy('table2_list')
    
    def get_service_detail(self, pk):
        return get_table2_detail(pk)
    
    def get_service_update(self, instance, data):
        return update_table2_service(instance, data)

class Table2DeleteView(BaseTableDeleteView):
    model = Table2
    success_url = reverse_lazy('table2_list')
    
    def get_service_detail(self, pk):
        return get_table2_detail(pk)
    
    def get_service_delete(self, instance):
        return delete_table2_service(instance)

#
## Table3 CRUD Views (Optimized Generic Views)
#

class Table3ListView(BaseTableListView):
    model = Table3
    
    def get_service_list(self):
        return get_table3_list()

class Table3DetailView(BaseTableDetailView):
    model = Table3
    
    def get_service_detail(self, pk):
        return get_table3_detail(pk)

class Table3CreateView(BaseTableCreateView):
    model = Table3
    form_class = Table3Form
    success_url = reverse_lazy('table3_list')
    
    def get_service_create(self, data):
        return create_table3_service(data)

class Table3UpdateView(BaseTableUpdateView):
    model = Table3
    form_class = Table3Form
    success_url = reverse_lazy('table3_list')
    
    def get_service_detail(self, pk):
        return get_table3_detail(pk)
    
    def get_service_update(self, instance, data):
        return update_table3_service(instance, data)

class Table3DeleteView(BaseTableDeleteView):
    model = Table3
    success_url = reverse_lazy('table3_list')
    
    def get_service_detail(self, pk):
        return get_table3_detail(pk)
    
    def get_service_delete(self, instance):
        return delete_table3_service(instance)
