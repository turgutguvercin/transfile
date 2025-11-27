from io import BytesIO
import os
from tabnanny import verbose
from django.core.files.base import ContentFile
from django.db import models
from django.utils import translation
from parler.models import TranslatableModel, TranslatedFields
from django.utils.text import slugify
from PIL import Image
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _

class Blog(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(max_length = 150, verbose_name=_("Blog Title")),
        content = RichTextField(verbose_name=_("Blog Content")),
        slug=models.SlugField(max_length=200, unique=True, verbose_name="Slug", blank=True, null=True),
        seo_title = models.CharField(max_length=255, verbose_name=_("SEO Title"), blank=True, null=True),
        seo_explanation = models.TextField(verbose_name=_("SEO Description"), blank=True, null=True)
    )
    image = models.ImageField(upload_to='blog_images/', verbose_name=_("Blog Image"), blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Register Date"))


    class Meta:
        verbose_name = _("Blog Yazısı")
        verbose_name_plural = _("Blog Yazıları")

    def save(self, *args, **kwargs):

        current_lang = translation.get_language()
        if not self.slug:
            self.slug = slugify(self.title)
            base_slug = self.slug
            num = 1
            while Blog.objects.filter(translations__slug=self.slug, translations__language_code=current_lang).exclude(pk=self.pk).exists():
                self.slug = f"{ base_slug}-{num}"
                num += 1
        

        if not self.seo_title:
            self.seo_title = self.title

        if not self.seo_explanation:
            self.seo_explanation = self.content[:150]


        super().save(*args, **kwargs)

        if self.image and not self.image.name.lower().endswith('.webp'):
            img_path = self.image.path
            img_name, _ = os.path.splitext(os.path.basename(img_path))
            img = Image.open(img_path).convert('RGB')


            webp_io = BytesIO()
            img.save(webp_io, format='WEBP', quality=85)
            webp_filename = f"{img_name}.webp"
            self.image.save(webp_filename, ContentFile(webp_io.getvalue()), save=False)

            detail_io = BytesIO()
            detail_img = img.copy()
            detail_img.thumbnail((800, 600))
            detail_img.save(detail_io, format='WEBP', quality=85)
            detail_folder = os.path.join('blog_images', 'detail')
            detail_path = os.path.join(detail_folder, f"{img_name}_detail.webp")
            full_detail_path = os.path.join(os.path.dirname(img_path), 'detail', f"{img_name}_detail.webp")
            os.makedirs(os.path.dirname(full_detail_path), exist_ok=True)
            with open(full_detail_path, 'wb') as f:
                f.write(detail_io.getvalue())


            list_io = BytesIO()
            list_img = img.copy()
            list_img.thumbnail((400, 300))
            list_img.save(list_io, format='WEBP', quality=85)
            list_folder = os.path.join('blog_images', 'list')
            list_path = os.path.join(list_folder, f"{img_name}_list.webp")
            full_list_path = os.path.join(os.path.dirname(img_path), 'list', f"{img_name}_list.webp")
            os.makedirs(os.path.dirname(full_list_path), exist_ok=True)
            with open(full_list_path, 'wb') as f:
                f.write(list_io.getvalue())


            if os.path.exists(img_path):
                os.remove(img_path)

  
            super().save(update_fields=['image'])

    def get_detail_image_url(self):
        if self.image:
            img_name, _ = os.path.splitext(os.path.basename(self.image.name))
            return f"/media/blog_images/detail/{img_name}_detail.webp"
        return ""
    
    def get_list_image_url(self):
        if self.image:
            img_name, _ = os.path.splitext(os.path.basename(self.image.name))
            return f"/media/blog_images/list/{img_name}_list.webp"
        return ""

    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        return title or (f"Blog #{self.pk}" if self.pk else "Blog")