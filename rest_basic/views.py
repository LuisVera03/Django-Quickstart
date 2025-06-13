from django.shortcuts import render, get_object_or_404, redirect
from .models import Table3, Table2, Table1
from django.http import HttpResponse, HttpResponseRedirect
import datetime

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
                return HttpResponse("Table3 created successfully.")
            except Exception as e:
                return HttpResponse(f"Error creating Table3: {e}")

        # --- Table2 ---
        elif form_type == 'table2':
            choice = request.POST.get('positive_small_int')
            try:
                Table2.objects.create(positive_small_int=int(choice))
                return HttpResponse("Table2 created successfully.")
            except Exception as e:
                return HttpResponse(f"Error creating Table2: {e}")

        # --- Table1 ---
        elif form_type == 'table1':
            print("x")
            try:
                #Django no acepta una cadena vacía ('') como un valor válido para campos que permiten null=True o blank=True. En esos casos, necesitas pasar None.
                foreign_key_id = request.POST.get('foreign_key') or None
                one_to_one_id = request.POST.get('one_to_one') or None
                many_to_many_ids = request.POST.get('many_to_many')
                print("c")
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
                print("B")
                # Many-to-many linking
                if many_to_many_ids:
                    print("a")
                    table3_objs = Table3.objects.filter(id__in=filter(None, many_to_many_ids))
                    table1.many_to_many.set(table3_objs)

                return HttpResponse("Table1 created successfully.")
            except Exception as e:
                return HttpResponse(f"Error creating Table1: {e}")
    else:
        #values_list() es un método de Django ORM que te permite extraer una o más columnas específicas
        #flat=True para obtener una lista simple en lugar de una lista de tuplas
        table2 = Table2.objects.values_list('id', flat=True)
        table3 = Table3.objects.values_list('id', flat=True)
        return render(request, 'add_data.html',{"table3":table3,"table2":table2})

def update_data(request):
    return render(request, 'update_data.html')

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
        return redirect('delete_data_2')
    # If an ID is provided in the request "GET", shows the confirmation
    elif request.GET.get('delete_id'):
        pk = request.GET.get('delete_id')
        deleting = get_object_or_404(Table1, pk=pk)

    return render(request, 'delete_data_2.html', {
        "records": records,
        "deleting": deleting,
    })

