from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import StructBlock, CharBlock, RichTextBlock

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