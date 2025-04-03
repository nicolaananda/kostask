from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User

class SignUpView(CreateView):
    """
    View for user registration.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # You can add additional logic here if needed
        return response

def login_view(request):
    """
    View for user login.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect admin users to admin dashboard
                if user.is_admin or user.is_staff:
                    return redirect('admin_dashboard')
                # Redirect regular users to user dashboard
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def dashboard(request):
    """
    View for user dashboard.
    """
    # Import here to avoid circular imports
    from tickets.models import Ticket
    
    # Get tickets for the current user
    tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    
    return render(request, 'accounts/dashboard.html', {'tickets': tickets})
