__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django import forms
from models import TavernaExecution

IMP_CHOICES = ()
from scs.views import search_resource
results = search_resource('Taverna')[0]
for result in results:
    if "Atomic Service" in str(result['type']):
        IMP_CHOICES += (result['local_id'], result['name']+' '+result['local_id']),

class TavernaExecutionForm(forms.ModelForm):

    class Meta:
        model = TavernaExecution
        exclude = ['owner', 't2flow', 'baclava', 'status', 'taverna_id', 'as_config_id', 'url', 'taverna_atomic_id']
        widgets = {
            'workflowId': forms.HiddenInput()
        }

    taverna_servers = forms.ChoiceField(label="Choice Taverna server", choices=IMP_CHOICES)
    taverna_url = forms.URLField(label="Custom Taverna endpoint", help_text="Set it only if you start an atomic service in development mode")
    default_inputs = forms.BooleanField(label="Default Inputs", help_text="Check if you want to run this workflow with your inputs")


    inputFile = forms.FileField(label="Input definition", help_text="Input definition file, *.xml")


