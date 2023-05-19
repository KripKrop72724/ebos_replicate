from django.forms import BaseInlineFormSet


class T10Alc11InlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(T10Alc11InlineFormSet, self).__init__(*args, **kwargs)
        try:
            for i, form in enumerate(self.forms):
                if not self.instance.alloc_lock_flag:
                    form.fields["debit_id"].disabled = True
                    form.fields["debit_vou"].disabled = True
                    form.fields["debit_ref"].disabled = True
                    form.fields["debit_open"].disabled = True
                    form.fields["debit_due_dt"].disabled = True
        except Exception as e:
            pass


class T10Alc12InlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(T10Alc12InlineFormSet, self).__init__(*args, **kwargs)
        try:
            for i, form in enumerate(self.forms):
                if not self.instance.alloc_lock_flag:
                    form.fields["credit_id"].disabled = True
                    form.fields["credit_vou"].disabled = True
                    form.fields["credit_ref"].disabled = True
                    form.fields["credit_open"].disabled = True
                    form.fields["credit_due_dt"].disabled = True
        except Exception as e:
            pass
