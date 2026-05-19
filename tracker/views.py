from django.shortcuts import render, redirect
from .forms import RegisterForm
from .forms import ExpenseForm
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
from django.db.models import Sum, Count
from django.db import models
import csv
from django.http import HttpResponse

def home(request):
    context = {}
    
    if request.user.is_authenticated:
        # Total expenses
        total_expenses = Expense.objects.filter(
            user=request.user
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Category breakdown
        category_data = Expense.objects.filter(
            user=request.user
        ).values('category').annotate(
            total=Sum('amount'),
            count=models.Count('id')
        ).order_by('-total')
        
        # This month expenses
        today = date.today()
        this_month_expenses = Expense.objects.filter(
            user=request.user,
            date__month=today.month,
            date__year=today.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Today expenses
        today_expenses = Expense.objects.filter(
            user=request.user,
            date=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Helping & Ministry total
        helping_ministry_total = Expense.objects.filter(
            user=request.user,
            category__in=['Helping', 'Ministry']
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Total number of expenses
        total_count = Expense.objects.filter(
            user=request.user
        ).count()
        
        # Recent expenses (last 5)
        recent_expenses = Expense.objects.filter(
            user=request.user
        ).order_by('-date')[:5]
        
        context = {
            'total_expenses': total_expenses,
            'category_data': category_data,
            'this_month_expenses': this_month_expenses,
            'today_expenses': today_expenses,
            'helping_ministry_total': helping_ministry_total,
            'total_count': total_count,
            'recent_expenses': recent_expenses,
        }
    
    return render(request, 'tracker/home_new.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'tracker/register_new.html', {'form': form})

@login_required
def add_expense(request):

    if request.method == 'POST':

        form = ExpenseForm(request.POST)

        if form.is_valid():

          expense = form.save(commit=False)

          expense.user = request.user

          # Only use prediction if category is "Other"
          if expense.category == 'Other':
              predicted_category = predict_category(expense.description)
              expense.category = predicted_category

          expense.save()

          return redirect('home')

    else:

        form = ExpenseForm()

    return render(
        request,
        'tracker/add_expense_new.html',
        {'form': form}
    )
@login_required
def expense_list(request):

    filter_type = request.GET.get('filter')

    expenses = Expense.objects.filter(
        user=request.user
    )

    today = date.today()

    if filter_type == 'today':

        expenses = expenses.filter(date=today)

    elif filter_type == 'week':

        week_ago = today - timedelta(days=7)

        expenses = expenses.filter(date__gte=week_ago)

    elif filter_type == 'month':

        expenses = expenses.filter(
            date__month=today.month,
            date__year=today.year
        )

    expenses = expenses.order_by('-date')
    
    # Get statistics for the cards
    total_expenses = Expense.objects.filter(
        user=request.user
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    category_data = Expense.objects.filter(
        user=request.user
    ).values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_count = Expense.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        'tracker/expense_list_new.html',
        {
            'expenses': expenses,
            'total_expenses': total_expenses,
            'category_data': category_data,
            'total_count': total_count,
        }
    )

@login_required
def expense_chart(request):

    expenses = Expense.objects.filter(
        user=request.user
    )

    category_data = expenses.values(
        'category'
    ).annotate(
        total=Sum('amount')
    )

    labels = []
    data = []

    for item in category_data:

        labels.append(item['category'])

        data.append(float(item['total']))

    return render(
        request,
        'tracker/expense_chart_new.html',
        {
            'labels': labels,
            'data': data
        }
    )

@login_required
def download_csv(request):

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Description',
        'Amount',
        'Category',
        'Date',
        'Notes'
    ])

    expenses = Expense.objects.filter(
        user=request.user
    )

    for expense in expenses:

        writer.writerow([
            expense.description,
            expense.amount,
            expense.category,
            expense.date,
            expense.notes
        ])

    return response

@login_required
def edit_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == 'POST':

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            return redirect('expense_list')

    else:

        form = ExpenseForm(instance=expense)

    return render(
        request,
        'tracker/edit_expense_new.html',
        {'form': form}
    )
@login_required
def delete_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id,
        user=request.user
    )

    if request.method == 'POST':

        expense.delete()

        return redirect('expense_list')

    return render(
        request,
        'tracker/delete_expense_new.html',
        {'expense': expense}
    )
def predict_category(description):

    description = description.lower()

    category_keywords = {

        'Food': [
            'pizza',
            'burger',
            'restaurant',
            'food',
            'coffee'
        ],

        'Travel': [
            'uber',
            'ola',
            'bus',
            'train',
            'flight'
        ],

        'Shopping': [
            'amazon',
            'flipkart',
            'shopping',
            'clothes'
        ],

        'Bills': [
            'electricity',
            'water',
            'internet',
            'recharge',
            'fees'
        ],

        'Entertainment': [
            'netflix',
            'movie',
            'spotify',
            'game'
        ],

        'Ministry': [
        'fund',
        'offering',
        'church',
        'ministry',
        'vbs',
        'mission'
    ],

    'Helping': [
        'helping',
        'donation',
        'charity',
        'orphanage',
        'support'
    ]
    }

    for category, keywords in category_keywords.items():

        for keyword in keywords:

            if keyword in description:

                return category

    return 'Other'