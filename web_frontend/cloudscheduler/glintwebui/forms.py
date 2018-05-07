from django import forms

class addRepoForm(forms.Form):
    cloud_name = forms.CharField(label="cloud_name", max_length=64)
    auth_url = forms.CharField(label="auth_url", max_length=256)
    tenant = forms.CharField(label="tenant", max_length=128)
    username = forms.CharField(label="username", max_length=64)
    password = forms.CharField(widget=forms.PasswordInput(), label="password", max_length=64)
    project_domain_name = forms.CharField(label="project_domain_name", max_length=64)
    user_domain_name = forms.CharField(label="user_domain_name", max_length=64,)
