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
from django.http import Http404, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

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
    """Base delete view with direct deletion and success/failure messaging."""
    success_url = None
    
    def get_object(self, queryset=None):
        obj = self.get_service_detail(self.kwargs['pk'])
        if not obj:
            raise Http404(f"{self.get_table_name()} record not found")
        return obj
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for direct deletion"""
        self.object = self.get_object()
        success = self.get_service_delete(self.object)
        if success:
            messages.success(request, f'{self.get_table_name()} record deleted successfully!')
        else:
            messages.error(request, 'Error deleting record')
        return redirect(self.get_success_url())
    
    def get(self, request, *args, **kwargs):
        """Redirect GET requests back to list view"""
        messages.warning(request, 'Invalid delete request. Use the delete button from the list.')
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
            self.request.session['active_app'] = 'lag'
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
    # Mark active app in session for cross-page consistency (e.g., flatpages)
    request.session['active_app'] = 'lag'
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


#
## API Views for CRUD operations (used by JavaScript frontend)
#

@method_decorator(csrf_exempt, name='dispatch')
class Table1APIView(LoginRequiredMixin, View):
    """API View for Table1 CRUD operations"""
    
    def get(self, request):
        """Get all Table1 records with related options"""
        try:
            table1_data = []
            table1_list = get_table1_list()
            
            for item in table1_list:
                # Serialize Table1 data
                data = {
                    'id': item.id,
                    'integer_field': item.integer_field,
                    'float_field': item.float_field,
                    'char_field': item.char_field,
                    'text_field': item.text_field,
                    'boolean_field': item.boolean_field,
                    'date_field': item.date_field.isoformat() if item.date_field else None,
                    'time_field': item.time_field.isoformat() if item.time_field else None,
                    'datetime_field': item.datetime_field.isoformat() if item.datetime_field else None,
                    'image_field': item.image_field.url if item.image_field else None,
                    'file_field': item.file_field.url if item.file_field else None,
                }
                
                # Handle relationships
                if item.foreign_key:
                    data['foreign_key'] = {
                        'id': item.foreign_key.id,
                        'positive_small_int': item.foreign_key.positive_small_int
                    }
                else:
                    data['foreign_key'] = None
                    
                if item.one_to_one:
                    data['one_to_one'] = {
                        'id': item.one_to_one.id,
                        'positive_small_int': item.one_to_one.positive_small_int
                    }
                else:
                    data['one_to_one'] = None
                    
                # Many to many
                data['many_to_many'] = []
                for m2m in item.many_to_many.all():
                    data['many_to_many'].append({
                        'id': m2m.id,
                        'email_field': m2m.email_field
                    })
                
                table1_data.append(data)
            
            # Get options for foreign keys
            table2_options = []
            for table2 in get_table2_list():
                table2_options.append({
                    'id': table2.id,
                    'positive_small_int': table2.positive_small_int
                })
                
            table3_options = []
            for table3 in get_table3_list():
                table3_options.append({
                    'id': table3.id,
                    'email_field': table3.email_field
                })
            
            return JsonResponse({
                'data': table1_data,
                'table2_options': table2_options,
                'table3_options': table3_options
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new Table1 record"""
        try:
            data = json.loads(request.body)
            
            # Process foreign_key and one_to_one fields (handle both formats)
            if 'foreign_key' in data and isinstance(data['foreign_key'], dict):
                data['foreign_key'] = data['foreign_key'].get('id')
            
            if 'one_to_one' in data and isinstance(data['one_to_one'], dict):
                data['one_to_one'] = data['one_to_one'].get('id')
            
            # Handle many-to-many separately
            many_to_many_data = data.pop('many_to_many', [])
            many_to_many_ids = []
            many_to_many_ids = []
            
            # Extract IDs from the many-to-many data (handle both formats)
            for item in many_to_many_data:
                if isinstance(item, dict) and 'id' in item:
                    many_to_many_ids.append(item['id'])
                else:
                    many_to_many_ids.append(item)
            
            # Create the record
            instance = create_table1_service(data)
            
            # Handle many-to-many relationships
            if many_to_many_ids:
                for m2m_id in many_to_many_ids:
                    table3_instance = get_table3_detail(m2m_id)
                    if table3_instance:
                        instance.many_to_many.add(table3_instance)
            
            return JsonResponse({'success': True, 'id': instance.id})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request):
        """Update Table1 record"""
        try:
            data = json.loads(request.body)
            instance_id = data.pop('id')
            
            instance = get_table1_detail(instance_id)
            if not instance:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            # Process foreign_key and one_to_one fields (handle both formats)
            if 'foreign_key' in data and isinstance(data['foreign_key'], dict):
                data['foreign_key'] = data['foreign_key'].get('id')
            
            if 'one_to_one' in data and isinstance(data['one_to_one'], dict):
                data['one_to_one'] = data['one_to_one'].get('id')
            
            # Handle many-to-many separately
            many_to_many_data = data.pop('many_to_many', [])
            many_to_many_ids = []
            many_to_many_ids = []
            
            # Extract IDs from the many-to-many data (handle both formats)
            for item in many_to_many_data:
                if isinstance(item, dict) and 'id' in item:
                    many_to_many_ids.append(item['id'])
                else:
                    many_to_many_ids.append(item)
            
            # Update the record
            updated_instance = update_table1_service(instance, data)
            
            # Handle many-to-many relationships
            updated_instance.many_to_many.clear()
            if many_to_many_ids:
                for m2m_id in many_to_many_ids:
                    table3_instance = get_table3_detail(m2m_id)
                    if table3_instance:
                        updated_instance.many_to_many.add(table3_instance)
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request):
        """Delete Table1 record"""
        try:
            data = json.loads(request.body)
            instance_id = data.get('id')
            
            instance = get_table1_detail(instance_id)
            if not instance:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            success = delete_table1_service(instance)
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Failed to delete record'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class Table2APIView(LoginRequiredMixin, View):
    """API View for Table2 CRUD operations"""
    
    def get(self, request):
        """Get all Table2 records"""
        try:
            table2_data = []
            table2_list = get_table2_list()
            
            for item in table2_list:
                data = {
                    'id': item.id,
                    'positive_small_int': item.positive_small_int,
                }
                table2_data.append(data)
            
            return JsonResponse({'data': table2_data})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new Table2 record"""
        try:
            data = json.loads(request.body)
            instance = create_table2_service(data)
            return JsonResponse({'success': True, 'id': instance.id})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request):
        """Update Table2 record"""
        try:
            data = json.loads(request.body)
            instance_id = data.pop('id')
            
            instance = get_table2_detail(instance_id)
            if not instance:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            updated_instance = update_table2_service(instance, data)
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request):
        """Delete Table2 record"""
        try:
            data = json.loads(request.body)
            instance_id = data.get('id')
            
            instance = get_table2_detail(instance_id)
            if not instance:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            success = delete_table2_service(instance)
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Failed to delete record'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class Table3APIView(LoginRequiredMixin, View):
    """API View for Table3 CRUD operations"""
    
    def get(self, request):
        """Get all Table3 records"""
        try:
            table3_data = []
            table3_list = get_table3_list()
            
            for item in table3_list:
                data = {
                    'id': item.id,
                    'duration_field': str(item.duration_field) if item.duration_field else None,
                    'email_field': item.email_field,
                }
                table3_data.append(data)
            
            return JsonResponse({'data': table3_data})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new Table3 record"""
        try:
            data = json.loads(request.body)
            instance = create_table3_service(data)
            return JsonResponse({'success': True, 'id': instance.id})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request):
        """Update Table3 record"""
        try:
            data = json.loads(request.body)
            instance_id = data.pop('id')
            
            instance = get_table3_detail(instance_id)
            if not instance:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            updated_instance = update_table3_service(instance, data)
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request):
        """Delete Table3 record"""
        try:
            data = json.loads(request.body)
            instance_id = data.get('id')
            
            instance = get_table3_detail(instance_id)
            if not instance:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
            success = delete_table3_service(instance)
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Failed to delete record'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


#
## Generic API Views (same data, different endpoint for distinction)
#

@method_decorator(csrf_exempt, name='dispatch')
class GenericTable1APIView(LoginRequiredMixin, View):
    """Generic API View for Table1 - uses the same logic but different URL"""
    
    def get(self, request):
        """Get all Table1 records using generic approach"""
        try:
            # Use the same Table1APIView logic
            api_view = Table1APIView()
            api_view.request = request
            return api_view.get(request)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new Table1 record using generic approach"""
        try:
            api_view = Table1APIView()
            api_view.request = request
            return api_view.post(request)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request):
        """Update Table1 record using generic approach"""
        try:
            api_view = Table1APIView()
            api_view.request = request
            return api_view.put(request)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request):
        """Delete Table1 record using generic approach"""
        try:
            api_view = Table1APIView()
            api_view.request = request
            return api_view.delete(request)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
