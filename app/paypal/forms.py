from django.templatetags.static import static
from paypal.standard.forms import PayPalPaymentsForm
from django.utils.html import format_html


def get_button_image():
    return 'http://www.paypal.com/en_US/i/btn/btn_paynowCC_LG.gif'


class ExtPayPalPaymentsForm(PayPalPaymentsForm):
    def render(self, *args, **kwargs):
        if not args and not kwargs:
            # `form.render` usage from template
            return format_html(
                """
                <form action="{0}" method="post" target="_parent">
                    {1}
                    <input type="image" src="{2}" name="submit" alt="Pay Now" />
                </form>
                """,
                self.get_login_url(),
                self.as_p(),
                get_button_image(),
            )
        else:
            # Need to delegate to super. This provides
            # support for `as_p` method and for `BoundField.label_tag`,
            # and perhaps others.
            return super().render(*args, **kwargs)
