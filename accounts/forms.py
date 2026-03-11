from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # lazy import models to avoid app registry issues at import time
        from cities_light.models import City, Country
        # add city field (ModelChoice). Resolve Country object first to avoid
        # unsupported lookup errors on the country relation.
        # django-cities-light Country uses `code2` for the 2-letter ISO code.
        usa = Country.objects.filter(code2__iexact='US').first()
        if usa:
            city_qs = City.objects.filter(country=usa).order_by('name')
        else:
            city_qs = City.objects.none()

        self.fields['city'] = forms.ModelChoiceField(
            queryset=city_qs,
            required=False,
            empty_label='Select city',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update( {'class': 'form-control'} )

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=commit)
        # Save or update profile with selected city and coords
        city = self.cleaned_data.get('city')
        try:
            profile = user.profile
        except Exception:
            from .models import Profile
            profile = Profile.objects.create(user=user)
        if city:
            profile.city = city
            # copy coordinates if present
            try:
                profile.latitude = city.latitude
                profile.longitude = city.longitude
            except Exception:
                pass
            profile.save()
        return user