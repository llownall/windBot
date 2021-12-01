from django import forms


class ExtendedForm(forms.BaseForm):
    """Mixin."""

    def as_div(self):
        """Return this form rendered as HTML <div>s."""
        return self._html_output(
            normal_row='<div%(html_class_attr)s data-form-row>%(label)s %(field)s%(help_text)s</div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )
