from django import forms
from enum import Enum

class Language(Enum):
    TURKISH = 'Turkish'
    ENGLISH = 'English'
    SPANISH = 'Spanish'
    FRENCH = 'French'
    GERMAN = 'German'

#LANG_CHOICES = [(lang.value, lang.value) for lang in Language]

LANG_CHOICES = []
for lang in Language:
    LANG_CHOICES.append((lang.value,lang.value))


class UploadFileForm(forms.Form):
    file = forms.FileField()
    source_lang = forms.ChoiceField(choices=LANG_CHOICES, initial=Language.TURKISH.value)
    target_lang = forms.ChoiceField(choices=LANG_CHOICES, initial=Language.ENGLISH.value)

    