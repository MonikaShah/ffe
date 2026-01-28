from wagtail.models import Page,Orderable
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks

from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel,InlinePanel
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

class GRPage(Page):
    custom_title = models.CharField(
        max_length=255,
        help_text="Title displayed on the page"
    )

    document = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload PDF or DOC file"
    )

    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
        FieldPanel('document'),
    ]

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