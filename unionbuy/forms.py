from django import forms


class TransForm(forms.Form):
    text = forms.CharField(label="分享文本")
    share_image = forms.ImageField(label="联盟原图")
