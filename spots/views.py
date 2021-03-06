from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView

from base.forms import ExtendedForm
from spots.models import Spot, Condition, FORM_WIND_DIRECTIONS


class SpotList(LoginRequiredMixin, ListView):
    model = Spot


class SpotForm(ExtendedForm, forms.ModelForm):
    class Meta:
        model = Spot
        exclude = ('image', 'creator')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'link_rp5': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SpotCreateView(LoginRequiredMixin, CreateView):
    model = Spot
    form_class = SpotForm
    success_url = reverse_lazy('spots_list')

    def get_context_data(self, **kwargs):
        data = super(SpotCreateView, self).get_context_data(**kwargs)
        data['is_create'] = True
        return data

    def form_valid(self, form):
        form.instance.creator = self.request.user.person
        return super(SpotCreateView, self).form_valid(form)


class SpotUpdateView(LoginRequiredMixin, UpdateView):
    model = Spot
    form_class = SpotForm
    success_url = reverse_lazy('spots_list')


class SpotDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        Spot.objects.filter(pk=pk).delete()
        return redirect('spots_list')


class ConditionList(LoginRequiredMixin, ListView):
    model = Condition

    def get_context_data(self, **kwargs):
        data = super(ConditionList, self).get_context_data(**kwargs)
        data['spot'] = Spot.objects.get(pk=self.kwargs['spot_id'])
        return data

    def get_queryset(self):
        queryset = super(ConditionList, self).get_queryset()
        return queryset.filter(spot_id=self.kwargs['spot_id']).order_by('-is_active', 'sequence_number')


class ConditionForm(ExtendedForm, forms.ModelForm):
    wind_directions = forms.MultipleChoiceField(
        label='?????????????????????? ??????????',
        widget=forms.CheckboxSelectMultiple(),
        choices=FORM_WIND_DIRECTIONS,
    )

    class Meta:
        model = Condition
        exclude = ('sequence_number', 'spot')

    def clean_wind_directions(self):
        wind_directions = self.cleaned_data['wind_directions']
        return list(map(int, wind_directions))

    def clean(self):
        super(ConditionForm, self).clean()

        if self.cleaned_data['wind_speed_min'] > self.cleaned_data['wind_speed_max']:
            raise ValidationError({'wind_speed_min': ['???????????? ?????????????? ?????????? ???? ?????????? ???????? ???????????? ??????????????']})

        if self.cleaned_data['temperature_min'] > self.cleaned_data['temperature_max']:
            raise ValidationError({'temperature_min': ['?????????????????????? ?????????????????????? ???? ?????????? ???????? ???????????? ????????????????????????']})


class ConditionCreateView(LoginRequiredMixin, CreateView):
    model = Condition
    form_class = ConditionForm
    
    def get_context_data(self, **kwargs):
        data = super(ConditionCreateView, self).get_context_data(**kwargs)
        data['is_create'] = True
        return data

    def get_success_url(self):
        return reverse_lazy('conditions_list', kwargs=dict(spot_id=self.kwargs['spot_id']))

    def form_valid(self, form):
        form.instance.spot = get_object_or_404(Spot, pk=self.kwargs['spot_id'])
        return super(ConditionCreateView, self).form_valid(form)


class ConditionUpdateView(LoginRequiredMixin, UpdateView):
    model = Condition
    form_class = ConditionForm

    def get_success_url(self):
        return reverse_lazy('conditions_list', kwargs=dict(spot_id=self.kwargs['spot_id']))


class ConditionDeleteView(LoginRequiredMixin, View):
    def get(self, request, spot_id, pk):
        Condition.objects.filter(pk=pk).delete()
        return redirect('conditions_list', spot_id)
