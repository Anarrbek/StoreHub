from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class':'input-field'}),
            'description': forms.Textarea(attrs={'rows':4,'class':'input-field'}),
            'price': forms.NumberInput(attrs={'class':'input-field','step':'0.01'}),
            'stock': forms.NumberInput(attrs={'class':'input-field'}),
            'category': forms.Select(attrs={'class':'input-field'}),
            'image': forms.ClearableFileInput(attrs={'class':'input-file'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


from django.contrib.auth import get_user_model
from django import forms as django_forms

User = get_user_model()


class RegisterForm(django_forms.ModelForm):
    password = django_forms.CharField(widget=django_forms.PasswordInput)
    password_confirm = django_forms.CharField(widget=django_forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise django_forms.ValidationError('Пароли не совпадают')
        return cleaned
