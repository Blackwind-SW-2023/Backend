from django.http import JsonResponse
import re, poplib, email
from email.header import decode_header, make_header
from django.views.decorators.csrf import csrf_exempt
import json

userid="dgistlogin"
userpw="komaruN12#$"

poplib._MAXLINE = 20480

def is_auth_mail(message):
    fr = make_header(decode_header(message.get('From')))
    subject = make_header(decode_header(message.get('Subject')))

    return (fr == 'no-reply@dgist.ac.kr') and (subject == '2차 인증 코드')

def get_auth_pop3(id, pw):
    # access to email server
    server = poplib.POP3_SSL('pop.naver.com',995)
    print(id)
    print(pw)
    server.user(id)
    server.pass_(pw)
    
    recent_no = server.stat()[0] # get total num of emails
    
    # traverse from the most recent message and find auth email
    message = None
    for i in range(recent_no):
        raw_email = b'\n'.join(server.retr(recent_no-i)[1]) # retrieve the whole message, join as binary
        message = email.message_from_bytes(raw_email) # Return a message object structure from a bytes-like object.
        if is_auth_mail(message): break
    
    # find auth code in the email by parsing
    text = message.get_payload(decode=True).decode(message.get_content_charset())
    auth_reg = re.search('<span>[0-9][0-9][0-9][0-9][0-9][0-9]</span>', text)
    auth_num = auth_reg.group().rstrip('</span>').lstrip('<span>')
    
    return auth_num

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # Load the JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        
        # Extract userId and userPw
        user_id = data.get('userId')
        user_pw = data.get('userPw')
        
        auth_num = get_auth_pop3(user_id, user_pw)
        
        # For now, just return the received userId and userPw as JSON response
        return JsonResponse(auth_num, safe=False)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

def send_message(request):
    data = {"message": get_auth_pop3(userid,userpw)}
    
    return JsonResponse(data)