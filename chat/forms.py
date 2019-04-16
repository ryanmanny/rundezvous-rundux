from django import forms

from chat.const import MAX_MESSAGE_LENGTH


class TextForm(forms.Form):
    """
    TextForm just allows user to enter arbitrary text
    TODO: Enforce character limit somehow?
    """
    text = forms.CharField(label='', max_length=MAX_MESSAGE_LENGTH)
