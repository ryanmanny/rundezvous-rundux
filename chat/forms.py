from django import forms

from chat import const


class TextForm(forms.Form):
    """
    TextForm just allows user to enter arbitrary text
    """
    text = forms.CharField(label='', max_length=const.MAX_MESSAGE_LENGTH)
