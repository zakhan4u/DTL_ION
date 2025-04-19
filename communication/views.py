from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note, UserProfile, NoteForwardHistory,InventoryItem,ItemRequest
from .forms import NoteForm, StatusUpdateForm, ForwardNoteForm,InventoryItemForm, ItemRequestForm
from django.contrib import messages



@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
        received_notes = Note.objects.filter(to_section=user_profile.section).order_by('-created_at')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not set up. Please contact the administrator.')
        received_notes = []
    
    sent_notes = Note.objects.filter(from_user=request.user).order_by('-created_at')
    if request.user.is_superuser:
        all_notes = Note.objects.all().order_by('-created_at')
    else:
        all_notes = None

    return render(request, 'communication/dashboard.html', {
        'sent_notes': sent_notes,
        'received_notes': received_notes,
        'all_notes': all_notes,
    })

@login_required
def inventory_list(request):
    items = InventoryItem.objects.all() if request.user.is_superuser else InventoryItem.objects.filter(added_by=request.user)
    return render(request, 'communication/inventory_list.html', {'items': items})

@login_required
def inventory_add(request):
    if request.user.userprofile.section != 'STANDARD' and not request.user.is_superuser:
        messages.error(request, "Only users in the Standard section can add inventory items.")
        return redirect('inventory_list')
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.added_by = request.user
            item.save()
            messages.success(request, f"Added {item.name} to inventory.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'communication/inventory_form.html', {'form': form, 'title': 'Add Inventory Item'})

@login_required
def inventory_edit(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if not request.user.is_superuser and item.added_by != request.user:
        messages.error(request, "You are not authorized to edit this item.")
        return redirect('inventory_list')
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {item.name} in inventory.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'communication/inventory_form.html', {'form': form, 'title': 'Edit Inventory Item'})

@login_required
def inventory_delete(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.user.userprofile.section != 'STANDARD' and not request.user.is_superuser:
        messages.error(request, "Only users in the Standard section can delete inventory items.")
        return redirect('inventory_list')
    if request.method == 'POST':
        item.delete()
        messages.success(request, f"Deleted {item.name} from inventory.")
        return redirect('inventory_list')
    return render(request, 'communication/inventory_confirm_delete.html', {'item': item})

@login_required
def stores_request(request):
    if request.user.userprofile.section == 'STANDARD' and not request.user.is_superuser:
        messages.error(request, "Standard section users manage inventory directly.")
        return redirect('inventory_list')
    query = request.GET.get('q')
    items = InventoryItem.objects.all()
    if query:
        items = items.filter(name__icontains=query) | items.filter(description__icontains=query)
    form = ItemRequestForm(initial={'item': items.first() if items.exists() else None})
    if request.method == 'POST':
        form = ItemRequestForm(request.POST)
        if form.is_valid():
            request_item = form.save(commit=False)
            request_item.requested_by = request.user
            request_item.status = 'APPROVED'
            try:
                request_item.save()
                messages.success(request, f"Requested {request_item.quantity} {request_item.item.name}.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('stores_request')
    requests = ItemRequest.objects.filter(requested_by=request.user)
    return render(request, 'communication/stores_request.html', {'form': form, 'requests': requests, 'items': items, 'query': query})
@login_required
def create_note(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not set up. Please contact the administrator.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.from_user = request.user
            note.save()
            messages.success(request, 'Note sent successfully!')
            return redirect('dashboard')
    else:
        form = NoteForm()
    return render(request, 'communication/create_note.html', {'form': form})

@login_required
def view_note(request, note_id):
    note = get_object_or_404(Note, unique_id=note_id)
    return render(request, 'communication/view_note.html', {'note': note})

@login_required
def update_status(request, note_id):
    note = get_object_or_404(Note, unique_id=note_id)
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not set up. Please contact the administrator.')
        return redirect('dashboard')

    if user_profile.section != note.to_section and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to update this note’s status.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status and comments updated successfully!')
            return redirect('dashboard')
    else:
        form = StatusUpdateForm(instance=note)
    
    return render(request, 'communication/update_status.html', {'form': form, 'note': note})

@login_required
def forward_note(request, note_id):
    note = get_object_or_404(Note, unique_id=note_id)
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not set up. Please contact the administrator.')
        return redirect('dashboard')

    if user_profile.section != note.to_section and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to forward this note.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ForwardNoteForm(request.POST)
        if form.is_valid():
            new_section = form.cleaned_data['to_section']
            comments = form.cleaned_data['comments']
            # Update note's to_section
            note.to_section = new_section
            if comments:
                note.receiver_comments = (note.receiver_comments or '') + '\n' + comments
            note.save()
            # Record forwarding history
            NoteForwardHistory.objects.create(
                note=note,
                from_section=user_profile.section,
                to_section=new_section,
                forwarded_by=request.user
            )
            messages.success(request, 'Note forwarded successfully!')
            return redirect('dashboard')
    else:
        form = ForwardNoteForm()
    
    return render(request, 'communication/forward_note.html', {'form': form, 'note': note})

@login_required
def request_approve(request, request_id):
    if request.user.userprofile.section != 'STANDARD' and not request.user.is_superuser:
        messages.error(request, "Only Standard section users can approve requests.")
        return redirect('inventory_list')
    item_request = get_object_or_404(ItemRequest, id=request_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        item_request.status = 'APPROVED' if action == 'approve' else 'REJECTED'
        try:
            item_request.save()
            messages.success(request, f"Request {item_request} {'approved' if action == 'approve' else 'rejected'}.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('inventory_list')
    return render(request, 'communication/request_approve.html', {'request': item_request})