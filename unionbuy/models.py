import re

from django.db import models
from django.conf import settings


class DateTimeModel(models.Model):
    created = models.DateTimeField("数据创建时间", auto_now_add=True)
    updated = models.DateTimeField("数据更新时间", auto_now=True)

    class Meta:
        abstract = True


class Share(DateTimeModel):
    SITE_TAOBAO = 1
    SITE_JD = 2
    SITE_SUNING = 3
    SITES = (
        (SITE_TAOBAO, "淘宝"),
        (SITE_JD, "京东"),
        (SITE_SUNING, "苏宁易购"),
    )
    site = models.SmallIntegerField("站点", choices=SITES, default=SITE_TAOBAO)
    code = models.SlugField("分享码", help_text="例如：淘口令")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="创建人")
    text = models.TextField("分享文案", blank=True)
    image = models.ImageField("分享图")

    def __str__(self):
        return re.split(r'\s+', self.text)[0]

    def get_absolute_url(self):
        import base64
        from django.urls import reverse

        url = reverse('code_show', kwargs={"code": str(base64.b64encode(self.code.encode('utf-8')), 'utf-8')})
        return url

    class Meta:
        verbose_name = "联盟分享"
        verbose_name_plural = verbose_name
        ordering = ('-created',)
        unique_together = (('site', 'code'),)
