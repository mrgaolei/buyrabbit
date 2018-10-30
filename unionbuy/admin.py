import re
from PIL import Image

from django.contrib import admin
from django.core.files.base import ContentFile
from django.utils.six import BytesIO

from unionbuy.models import Share


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    readonly_fields = ('creator', 'code')
    list_display = ('__str__', 'code', 'image', 'creator', 'created')
    search_fields = ('text', '=code')

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f in self.model._meta.fields]
        else:
            return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
            # 先处理文本中的码
            code = re.findall('[a-zA-Z0-9]{11}', form.cleaned_data['text'])
            obj.code = code[0]
            # 生成领码url
            url = f"http://{request.get_host()}{obj.get_absolute_url()}"

            # 再处理图片
            image = Image.open(obj.image)
            print(image.size)
            if image.size[0] == 800:
                # iPhone X size
                box = [495, 840]
                box_size = 7
                border = 1
            else:
                # Android size
                box = [575, 945]
                box_size = 7
                border = 2

            import qrcode
            qr = qrcode.QRCode(box_size=box_size, border=border)
            qr.add_data(url)
            img = qr.make_image()

            image.paste(img, box)
            image.load()
            image = image.convert("RGB")

            img_io = BytesIO()
            image.save(img_io, format='JPEG')
            content = ContentFile(img_io.getvalue(), f'{obj.code}.jpg')
            obj.image = content

        super().save_model(request, obj, form, change)
