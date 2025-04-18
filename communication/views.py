from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note, UserProfile, NoteForwardHistory
from .forms import NoteForm, StatusUpdateForm, ForwardNoteForm
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