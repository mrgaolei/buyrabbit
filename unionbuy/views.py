import base64
import re
# import zbarlight
from PIL import Image

from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

from .forms import TransForm


def home(request):
    
    form = TransForm()
    
    return render(request, 'home.html', {'form': form})


def search(request, q):
    return render(request, 'search.html')


def unicon_image(request):
    if request.method == 'POST':
        form = TransForm(request.POST, request.FILES)
        if form.is_valid():
            # 先处理文本中的码
            code = re.findall('[a-zA-Z0-9]{11}', form.cleaned_data['text'])
            code = f"₴{code[0]}₴"
            # 生成领码url
            url = reverse('code_show', kwargs={"code": str(base64.b64encode(code.encode('utf-8')), 'utf-8')})
            url = f"http://{request.get_host()}{url}"
            print(url)
            # 生成url二维码
            
            # 再处理图片
            image = Image.open(form.cleaned_data['share_image'])
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
            # codes = zbarlight.scan_codes(['qrcode'], image)
            # print('QR codes: %s' % codes)

            response = HttpResponse(content_type="image/jpeg")
            image = image.convert("RGB")
            image.save(response, "JPEG")
            return response


def code_show(request, code):
    try:
        code = str(base64.b64decode(code), 'utf-8')
    except ValueError:
        return HttpResponseBadRequest("编码错误")
    return render(request, 'code_show.html', {'code': f"₴{code}₴"})
