from django.shortcuts import render, get_object_or_404, redirect
from .models import Table3, Table2, Table1
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.contrib import messages
from django.utils.dateparse import parse_duration

from .forms import Table1Form, Table2Form, Table3Form

# Create your views here.
def index(request):
    return render(request, 'index.html')

def rest_basic(request):
    return render(request, 'rest_basic.html')

def crud(request):
    return render(request, 'crud.html')

def get_data(request):
    table3 = Table3.objects.all()
    table2 = Table2.objects.all()
    table1 = Table1.objects.all()
    return render(request, 'get_data.html',{"table3":table3,"table2":table2,"table1":table1})

def add_data(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # --- Table3 ---
        if form_type == 'table3':
            duration = request.POST.get('duration_field')
            email = request.POST.get('email_field')

            try:
                # Convert to timedelta if needed
                days, time_part = duration.strip().split(' ')
                hours, minutes, seconds = map(int, time_part.split(':'))
                duration_td = datetime.timedelta(days=int(days), hours=hours, minutes=minutes, seconds=seconds)

                Table3.objects.create(duration_field=duration_td, email_field=email)
                messages.success(request, "Table3 created successfully.")
                return redirect('add_data')
            except Exception as e:
                messages.error(request, f"Error creating Table3: {e}")
                return redirect('add_data')

        # --- Table2 ---
        elif form_type == 'table2':
            choice = request.POST.get('positive_small_int')
            try:
                Table2.objects.create(positive_small_int=int(choice))
                messages.success(request, "Table2 created successfully.")
                return redirect('add_data')
            except Exception as e:
                messages.error(request, f"Error creating Table2: {e}")
                return redirect('add_data')

        # --- Table1 ---
        elif form_type == 'table1':
            try:
                #Django no acepta una cadena vacía ('') como un valor válido para campos que permiten null=True o blank=True. En esos casos, necesitas pasar None.
                foreign_key_id = request.POST.get('foreign_key') or None
                one_to_one_id = request.POST.get('one_to_one') or None
                many_to_many_ids = request.POST.get('many_to_many')
                table1 = Table1.objects.create(
                    foreign_key_id=foreign_key_id or None,
                    one_to_one_id=one_to_one_id or None,
                    integer_field=request.POST.get('integer_field') or None,
                    float_field=request.POST.get('float_field') or None,
                    char_field=request.POST.get('char_field'),
                    text_field=request.POST.get('text_field', ''),
                    boolean_field=bool(request.POST.get('boolean_field')),
                    date_field=request.POST.get('date_field') or None,
                    time_field=request.POST.get('time_field') or None,
                    datetime_field=request.POST.get('datetime_field') or None,
                    image_field=request.FILES.get('image_field'),
                    file_field=request.FILES.get('file_field'),
                )
                # Many-to-many linking
                if many_to_many_ids:
                    table3_objs = Table3.objects.filter(id__in=filter(None, many_to_many_ids))
                    table1.many_to_many.set(table3_objs)

                messages.success(request, "Table1 created successfully.")
                return redirect('add_data')
            except Exception as e:
                messages.error(request, f"Error creating Table1: {e}")
                return redirect('add_data')
    else:
        #values_list() es un método de Django ORM que te permite extraer una o más columnas específicas
        #flat=True para obtener una lista simple en lugar de una lista de tuplas
        table2 = Table2.objects.values_list('id', flat=True)
        table3 = Table3.objects.values_list('id', flat=True)
        return render(request, 'add_data.html',{"table3":table3,"table2":table2})

def update_data(request):
    table1 = Table1.objects.all()
    table2 = Table2.objects.all()
    table3 = Table3.objects.all()
    table2_ids = Table2.objects.values_list('id', flat=True)
    table3_ids = Table3.objects.values_list('id', flat=True)

    editing = None
    editing_table = None
    selected_many = []

    # Manejo de POST: guardar cambios
    if request.method == 'POST' and request.POST.get('edit_id') and request.POST.get('edit_table'):
        pk = request.POST.get('edit_id')
        edit_table = request.POST.get('edit_table')

        try:
            if edit_table == 'table1':
                editing = get_object_or_404(Table1, pk=pk)
                editing_table = 'table1'
                editing.foreign_key_id = request.POST.get('foreign_key') or None
                editing.one_to_one_id = request.POST.get('one_to_one') or None
                editing.integer_field = request.POST.get('integer_field') or None
                editing.float_field = request.POST.get('float_field') or None
                editing.char_field = request.POST.get('char_field')
                editing.text_field = request.POST.get('text_field', '')
                editing.boolean_field = bool(request.POST.get('boolean_field'))
                editing.date_field = request.POST.get('date_field') or None
                editing.time_field = request.POST.get('time_field') or None
                editing.datetime_field = request.POST.get('datetime_field') or None
                # Archivos
                if request.FILES.get('image_field'):
                    editing.image_field = request.FILES.get('image_field')
                if request.FILES.get('file_field'):
                    editing.file_field = request.FILES.get('file_field')
                editing.save()
                # ManyToMany
                many_to_many_ids = request.POST.getlist('many_to_many')
                if many_to_many_ids:
                    table3_objs = Table3.objects.filter(id__in=filter(None, many_to_many_ids))
                    editing.many_to_many.set(table3_objs)
                else:
                    editing.many_to_many.clear()
                messages.success(request, "Table1 updated successfully.")
            elif edit_table == 'table2':
                editing = get_object_or_404(Table2, pk=pk)
                editing_table = 'table2'
                editing.positive_small_int = request.POST.get('positive_small_int')
                editing.save()
                messages.success(request, "Table2 updated successfully.")
            elif edit_table == 'table3':
                editing = get_object_or_404(Table3, pk=pk)
                editing_table = 'table3'
                editing.duration_field = parse_duration(request.POST.get('duration_field'))
                editing.email_field = request.POST.get('email_field')
                editing.save()
                messages.success(request, "Table3 updated successfully.")
            return redirect('update_data')
        except Exception as e:
            messages.error(request, f"Error updating: {e}")
            return render(request, 'update_data.html', {
                "table1": table1,
                "table2": table2,
                "table3": table3,
                "editing": editing,
                "editing_table": editing_table,
                "selected_many": selected_many,
                "table2_ids": table2_ids,
                "table3_ids": table3_ids,
                "error": str(e),
            })

    # Manejo de GET: mostrar formulario de edición
    elif request.GET.get('edit_id') and request.GET.get('edit_table'):
        pk = request.GET.get('edit_id')
        editing_table = request.GET.get('edit_table')
        if editing_table == 'table1':
            editing = get_object_or_404(Table1, pk=pk)
            selected_many = list(editing.many_to_many.values_list('id', flat=True))
        elif editing_table == 'table2':
            editing = get_object_or_404(Table2, pk=pk)
        elif editing_table == 'table3':
            editing = get_object_or_404(Table3, pk=pk)

    return render(request, 'update_data.html', {
        "table1": table1,
        "table2": table2,
        "table3": table3,
        "editing": editing,
        "editing_table": editing_table,
        "selected_many": selected_many,
        "table2_ids": table2_ids,
        "table3_ids": table3_ids,
    })

def delete_data_1(request):
    active_items = Table1.objects.filter(boolean_field=True)
    inactive_items = Table1.objects.filter(boolean_field=False)
    deleting = None

    # If a POST request is received with a delete_id, set the record as inactive
    if request.method == 'POST' and request.POST.get('delete_id'):
        pk = request.POST.get('delete_id')
        entry = get_object_or_404(Table1, pk=pk)
        entry.boolean_field = False  # Mark as inactive
        entry.save()
        messages.success(request, "Record disabled successfully.")
        return redirect('delete_data_1')

    # If a GET request is received with a delete_id, show the confirmation prompt
    elif request.GET.get('delete_id'):
        pk = request.GET.get('delete_id')
        deleting = get_object_or_404(Table1, pk=pk)

    # Render the template with both active and inactive items and the item to confirm disabling
    return render(request, 'delete_data_1.html', {
        "active_items": active_items,
        "inactive_items": inactive_items,
        "deleting": deleting,
    })

def delete_data_2(request):
    records = Table1.objects.all()
    deleting = None

    if request.method == 'POST' and request.POST.get('delete_id'):
        pk = request.POST.get('delete_id')
        entry = get_object_or_404(Table1, pk=pk)
       # Delete associated files if they exist
        if entry.image_field:
            entry.image_field.delete(save=False)
        if entry.file_field:
            entry.file_field.delete(save=False)
        entry.delete()
        messages.success(request, "Record permanently deleted.")
        return redirect('delete_data_2')
    # If an ID is provided in the request "GET", shows the confirmation
    elif request.GET.get('delete_id'):
        pk = request.GET.get('delete_id')
        deleting = get_object_or_404(Table1, pk=pk)

    return render(request, 'delete_data_2.html', {
        "records": records,
        "deleting": deleting,
    })

def crud_form(request):
    return render(request, 'crud_form.html')

def get_data_form(request):
    table3 = Table3.objects.all()
    table2 = Table2.objects.all()
    table1 = Table1.objects.all()
    return render(request, 'get_data_form.html',{"table3":table3,"table2":table2,"table1":table1})


def form(request,table):
    form_class = None
    model_name = ""
    
    if table == "table1":
        form_class = Table1Form
        model_name = "Table1"
    elif table == "table2":
        form_class = Table2Form
        model_name = "Table2"
    elif table == "table3":
        form_class = Table3Form
        model_name = "Table3"
    else:
        return HttpResponse("Table is not valid", status=400)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"{model_name} created successfully.")
            return redirect(add_data_form)
        else:
            messages.error(request, "Invalid form.")
    else:
        form = form_class()

    return render(request, 'form.html', {'form': form, 'model_name': model_name})

def add_data_form(request):
    return render(request, 'add_data_form.html',)

def update_form(request,table,id):
    form_class = None
    model_name = ""
    
    if table == "table1":
        form_class = Table1Form
        model_name = "Table1"
        obj = get_object_or_404(Table1, pk=id)
    elif table == "table2":
        form_class = Table2Form
        model_name = "Table2"
        obj = get_object_or_404(Table2, pk=id)
    elif table == "table3":
        form_class = Table3Form
        model_name = "Table3"
        obj = get_object_or_404(Table3, pk=id)
    else:
        return HttpResponse("Table is not valid", status=400)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{model_name} updated successfully.")
            return redirect(update_data_form)
        else:
            messages.error(request, "Invalid form.")
    else:
        form = form_class(instance=obj)

    return render(request, 'form.html', {'form': form, 'model_name': model_name})

def update_data_form(request):
    table3 = Table3.objects.all()
    table2 = Table2.objects.all()
    table1 = Table1.objects.all()
    return render(request, 'update_data_form.html',{"table3":table3,"table2":table2,"table1":table1})

