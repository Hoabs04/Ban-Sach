from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Address
from .forms import UserProfileForm, AddressForm


@login_required
def profile(request):
    """View user profile."""
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Cập nhật hồ sơ thành công!'))
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def address_list(request):
    """List all addresses."""
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_create(request):
    """Create a new address."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, _('Thêm địa chỉ thành công!'))
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': _('Thêm địa chỉ mới')})


@login_required
def address_edit(request, pk):
    """Edit an address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Cập nhật địa chỉ thành công!'))
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': _('Sửa địa chỉ')})


@login_required
def address_delete(request, pk):
    """Delete an address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, _('Xóa địa chỉ thành công!'))
    return redirect('accounts:address_list')


@login_required
def my_orders(request):
    """View order history."""
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})
