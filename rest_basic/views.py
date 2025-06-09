from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def crud(request):
    return render(request, 'crud.html')

def get_data(request):
    return render(request, 'get_data.html')

def add_data(request):
    return render(request, 'add_data.html')

def update_data(request):
    return render(request, 'update_data.html')

def delete_data_1(request):
    return render(request, 'delete_data_1.html')

def delete_data_2(request):
    return render(request, 'delete_data_2.html')

