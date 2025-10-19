"""Layer and Generic app views.

Provides:
1. Auth flows (Login, Register, Logout)
2. Dashboard view aggregating counts
3. Generic CRUD views for Table1, Table2, Table3
4. Clear separation: Views -> Services -> Repositories -> ORM
"""

from django.shortcuts import redirect
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import LoginForm, RegisterForm, Table1Form, Table2Form, Table3Form
from rest.models import Table1, Table2, Table3
from .services import (
    try_login,
    register_user,
    perform_logout,
    Table1Service,
    Table2Service,
    Table3Service,
    get_dashboard_data,
)

#
# Base Mixins for CRUD
#


class BaseTableMixin:
    """Common context + URL name helpers for CRUD views."""

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_name"] = self.get_table_name()
        context.update(self.get_url_names())

        # Add sidebar counters for consistent display
        dashboard_data = get_dashboard_data()
        context["total_table1"] = dashboard_data["table1_count"]
        context["total_table2"] = dashboard_data["table2_count"]
        context["total_table3"] = dashboard_data["table3_count"]

        return context

    def get_table_name(self):
        return self.model.__name__

    def get_url_names(self):
        table_name = self.model.__name__.lower()
        return {
            "list_url": f"{table_name}_list",
            "detail_url": f"{table_name}_detail",
            "create_url": f"{table_name}_create",
            "update_url": f"{table_name}_update",
            "delete_url": f"{table_name}_delete",
        }


class BaseTableListView(LoginRequiredMixin, BaseTableMixin, ListView):
    template_name = "Generic_templates/table.html"
    context_object_name = "object_list"
    paginate_by = 25

    def get_queryset(self):
        return self.service.list().order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get formatted data for each object
        object_list = []
        for obj in context["object_list"]:
            object_data = {
                "id": obj.id,
                "fields": self.service.get_field_data(obj),
                "object": obj,  # Keep original object for URLs
            }
            object_list.append(object_data)
        context["object_list"] = object_list
        return context


class BaseTableDetailView(LoginRequiredMixin, BaseTableMixin, DetailView):
    template_name = "Generic_templates/detail.html"
    context_object_name = "object"

    def get_object(self, queryset=None):
        obj = self.service.detail(self.kwargs["pk"])
        if not obj:
            raise Http404(f"{self.get_table_name()} not found")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add fields data to context for template rendering
        context["fields"] = self.service.get_field_data(self.object)
        return context


class BaseTableCreateView(LoginRequiredMixin, BaseTableMixin, CreateView):
    template_name = "Generic_templates/form.html"

    def form_valid(self, form):
        try:
            self.object = self.service.create(**form.cleaned_data)
            messages.success(
                self.request, f"{self.get_table_name()} created successfully!"
            )
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Error creating record: {str(e)}")
            return self.form_invalid(form)


class BaseTableUpdateView(LoginRequiredMixin, BaseTableMixin, UpdateView):
    template_name = "Generic_templates/form.html"

    def get_object(self, queryset=None):
        obj = self.service.detail(self.kwargs["pk"])
        if not obj:
            raise Http404(f"{self.get_table_name()} not found")
        return obj

    def form_valid(self, form):
        try:
            self.object = self.service.update(self.object.pk, **form.cleaned_data)
            messages.success(
                self.request, f"{self.get_table_name()} updated successfully!"
            )
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Error updating record: {str(e)}")
            return self.form_invalid(form)


class BaseTableDeleteView(LoginRequiredMixin, BaseTableMixin, DeleteView):
    success_url = None

    def get_object(self, queryset=None):
        obj = self.service.detail(self.kwargs["pk"])
        if not obj:
            raise Http404(f"{self.get_table_name()} not found")
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.service.delete(self.object.pk)
            messages.success(request, f"{self.get_table_name()} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting record: {str(e)}")
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        messages.warning(request, "Invalid delete request. Use the delete button.")
        return redirect(self.get_success_url())


#
# Auth Views
#


class LoginView(FormView):
    template_name = "LAG/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("home_layer_and_generic")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home_layer_and_generic")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if try_login(self.request, **form.cleaned_data):
            # Save current app in session
            self.request.session['current_app'] = 'layer_and_generic'
            self.request.session['home_url'] = 'home_layer_and_generic'
            self.request.session['logout_url'] = 'logout_layer_and_generic'
            return super().form_valid(form)
        messages.error(self.request, "Incorrect username or password")
        return self.form_invalid(form)


class RegisterView(FormView):
    template_name = "LAG/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login_layer_and_generic")

    def form_valid(self, form):
        user = register_user(**form.cleaned_data)
        if user:
            messages.success(self.request, "User created successfully")
            return super().form_valid(form)
        messages.error(self.request, "User already exists")
        return self.form_invalid(form)


class LogoutView(View):
    def post(self, request):
        perform_logout(request)
        return redirect("login_layer_and_generic")


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "LAG/home.html"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add dashboard data for home page stats
        dashboard_data = get_dashboard_data()
        context.update(dashboard_data)

        # Add sidebar counters (these variables are used in base.html)
        context["total_table1"] = dashboard_data["table1_count"]
        context["total_table2"] = dashboard_data["table2_count"]
        context["total_table3"] = dashboard_data["table3_count"]
        return context


#
# Table1 Views (legacy URL names kept)
#


class Table1ListView(BaseTableListView):
    model = Table1
    service = Table1Service

    def get_url_names(self):
        return {
            "list_url": "list",
            "detail_url": "detail",
            "create_url": "create",
            "update_url": "update",
            "delete_url": "delete",
        }


class Table1DetailView(BaseTableDetailView):
    model = Table1
    service = Table1Service

    def get_url_names(self):
        return {
            "list_url": "list",
            "detail_url": "detail",
            "create_url": "create",
            "update_url": "update",
            "delete_url": "delete",
        }


class Table1CreateView(BaseTableCreateView):
    model = Table1
    form_class = Table1Form
    service = Table1Service
    success_url = reverse_lazy("list")

    def get_url_names(self):
        return {
            "list_url": "list",
            "detail_url": "detail",
            "create_url": "create",
            "update_url": "update",
            "delete_url": "delete",
        }


class Table1UpdateView(BaseTableUpdateView):
    model = Table1
    form_class = Table1Form
    service = Table1Service
    success_url = reverse_lazy("list")

    def get_url_names(self):
        return {
            "list_url": "list",
            "detail_url": "detail",
            "create_url": "create",
            "update_url": "update",
            "delete_url": "delete",
        }


class Table1DeleteView(BaseTableDeleteView):
    model = Table1
    service = Table1Service
    success_url = reverse_lazy("list")

    def get_url_names(self):
        return {
            "list_url": "list",
            "detail_url": "detail",
            "create_url": "create",
            "update_url": "update",
            "delete_url": "delete",
        }


#
# Table2 Views
#


class Table2ListView(BaseTableListView):
    model = Table2
    service = Table2Service


class Table2DetailView(BaseTableDetailView):
    model = Table2
    service = Table2Service


class Table2CreateView(BaseTableCreateView):
    model = Table2
    form_class = Table2Form
    service = Table2Service
    success_url = reverse_lazy("table2_list")


class Table2UpdateView(BaseTableUpdateView):
    model = Table2
    form_class = Table2Form
    service = Table2Service
    success_url = reverse_lazy("table2_list")


class Table2DeleteView(BaseTableDeleteView):
    model = Table2
    service = Table2Service
    success_url = reverse_lazy("table2_list")


#
# Table3 Views
#


class Table3ListView(BaseTableListView):
    model = Table3
    service = Table3Service


class Table3DetailView(BaseTableDetailView):
    model = Table3
    service = Table3Service


class Table3CreateView(BaseTableCreateView):
    model = Table3
    form_class = Table3Form
    service = Table3Service
    success_url = reverse_lazy("table3_list")


class Table3UpdateView(BaseTableUpdateView):
    model = Table3
    form_class = Table3Form
    service = Table3Service
    success_url = reverse_lazy("table3_list")


class Table3DeleteView(BaseTableDeleteView):
    model = Table3
    service = Table3Service
    success_url = reverse_lazy("table3_list")
