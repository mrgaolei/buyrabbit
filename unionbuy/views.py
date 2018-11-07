import base64
import re
import requests
# import zbarlight

from PIL import Image
from datetime import timedelta
from urllib import parse

from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User

from unionbuy.models import ThirdAuth
from .forms import TransForm


client_id = settings.TAOBAO_CLIENT_ID
client_secret = settings.TAOBAO_CLIENT_SECRET


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
            if image.size[0] in [800, 1000]:
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


def third_auth(request):
    uri = request.build_absolute_uri(reverse('auth_callback'))
    url = f"https://oauth.taobao.com/authorize?response_type=code&client_id={client_id}&redirect_uri={uri}&state=&view=wap"
    return redirect(url)


def auth_back(request):
    code = request.GET['code']
    url = 'https://oauth.taobao.com/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.build_absolute_uri(reverse('auth_callback')),
        'view': 'wap',
    }
    r = requests.post(url, data=data)
    if r.status_code == 200:
        resp = r.json()
        try:
            third = ThirdAuth.objects.get(third=ThirdAuth.THIRD_TAOBAO, third_uid=resp['taobao_user_id'])
            user = third.user
        except ThirdAuth.DoesNotExist:
            user = User.objects.create_user(parse.unquote(resp['taobao_user_nick']), **{'is_staff': True})
            ThirdAuth.objects.create(
                user=user,
                third=ThirdAuth.THIRD_TAOBAO,
                third_uid=resp['taobao_user_id'],
                access_token=resp['access_token'],
                expires_in=timezone.now() + timedelta(seconds=int(resp['expires_in'])),
            )
        login(request, user)
        return redirect('/admin/')
    else:
        return HttpResponseBadRequest(r.text)
