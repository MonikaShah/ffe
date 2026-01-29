import requests
from django.conf import settings
from wagtail.models import Page,Orderable
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from django.http import JsonResponse
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel,InlinePanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.blocks import StructBlock, CharBlock, RichTextBlock,URLBlock
from django.db import models
from wagtail.documents.models import Document
from modelcluster.fields import ParentalKey
class HomePage(Page):
    """
    CMS container home page.
    Not used for rendering the Django home view.
    """
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["content.AchievementPage"]

    content_panels = Page.content_panels

class SimplePage(Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
class AchievementBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=True,
        help_text="Achievement heading (plain text)"
    )

    description = blocks.RichTextBlock(
        features=[
            "h3",        # section heading
            "bold",
            "italic",
            "ul",
            "ol",
            "link"
        ],
        help_text="Use toolbar for headings and lists"
    )

    image = ImageChooserBlock(
        required=False,
        help_text="Optional supporting image"
    )

    class Meta:
        icon = "award"
        label = "Achievement"
        template = "blocks/achievement_block.html"


class AchievementPage(Page):
    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"]
    )

    achievements = StreamField(
        [
            ("achievement", AchievementBlock()),
        ],
        blank=True,
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("achievements"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

class MediaUpdateBlock(StructBlock):
    title = CharBlock(
        required=True,
        help_text="Media headline / title"
    )

    media_link = URLBlock(
        required=False,
        help_text="Link to news article (optional)"
    )

    video_embed = RichTextBlock(
        required=False,
        features=["embed"],
        help_text="Paste YouTube / video embed"
    )

    thumbnail = ImageChooserBlock(
        required=False,
        help_text="Optional thumbnail image"
    )

    class Meta:
        icon = "media"
        label = "Media Update"


class MediaUpdatesPage(Page):
    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"]
    )

    media_updates = StreamField(
        [
            ("media", MediaUpdateBlock()),
        ],
        blank=True,
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("media_updates"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []
class GRDocument(Orderable):
    page = ParentalKey(
        'GRPage',
        on_delete=models.CASCADE,
        related_name='gr_documents'
    )

    title = models.CharField(
        max_length=255,
        help_text="Document title shown to users"
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('document'),
    ]

class GRPage(Page):
    custom_title = models.CharField(
        max_length=255,
        help_text="Title displayed on the page"
    )

    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
        InlinePanel('gr_documents', label="GR Documents"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []


class RTIDocument(Orderable):
    page = ParentalKey(
        'RTIPage',
        on_delete=models.CASCADE,
        related_name='rti_documents'
    )

    title = models.CharField(
        max_length=255,
        help_text="Document title shown to users"
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('document'),
    ]
    
class RTIPage(Page):
    custom_title = models.CharField(
        max_length=255,
        help_text="Title displayed on the page"
    )

    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
        InlinePanel('rti_documents', label="RTI Documents"),
    ]
class ContactFormField(AbstractFormField):
    page = ParentalKey(
        'ContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields'
    )
class ContactPage(AbstractEmailForm):
    template = "content/contact_page.html"

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    google_map_embed = models.TextField(
        blank=True,
        help_text="Paste Google Maps iframe embed code"
    )

    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Example: 919876543210"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form Fields"),
        FieldPanel('address'),
        FieldPanel('phone'),
        FieldPanel('email'),
        FieldPanel('google_map_embed'),
        FieldPanel('whatsapp_number'),
        FieldPanel('thank_you_text'),
        FormSubmissionsPanel(),
        FieldPanel('to_address'),
        FieldPanel('from_address'),
        FieldPanel('subject'),
    ]

    # ✅ Correct place to add template variables
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["RECAPTCHA_PUBLIC_KEY"] = settings.RECAPTCHA_PUBLIC_KEY
        return context

    # ✅ Only override serve for AJAX logic
    def serve(self, request):
        if (
            request.method == "POST"
            and request.headers.get("x-requested-with") == "XMLHttpRequest"
        ):
            recaptcha_response = request.POST.get("g-recaptcha-response")

            data = {
                "secret": settings.RECAPTCHA_PRIVATE_KEY,
                "response": recaptcha_response,
                "remoteip": request.META.get("REMOTE_ADDR"),
            }

            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data=data,
                timeout=5,
            )
            result = r.json()

            if not result.get("success"):
                return JsonResponse(
                    {"success": False, "error": "Invalid reCAPTCHA"},
                    status=400,
                )

            # process form normally (email + DB save)
            super().serve(request)

            return JsonResponse({"success": True})

        # ✅ NORMAL Wagtail rendering
        return super().serve(request)
