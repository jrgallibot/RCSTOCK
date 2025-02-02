from django import forms

from app.backend.models import TblGeneralInfo
from app.models import Shop


class UploadLogoForm(forms.ModelForm):
    class Meta:
        model = TblGeneralInfo
        fields = ['picture']


class UploadShopLogoForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['logo']