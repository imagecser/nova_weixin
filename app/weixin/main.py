# -*- coding:utf8 -*-
# Author: shizhenyu96@gamil.com
# github: https://github.com/imndszy
import time
import hashlib
import xml.etree.ElementTree as ET
from flask import request, make_response, redirect, render_template, session,jsonify

from nova_weixin.app.weixin import weixin
from nova_weixin.app.weixin.weixinconfig import TOKEN
# from nova_weixin.app.weixin.oauth_handler import jiaowu,get_openid,jiaowu_save


@weixin.route('/', methods=['GET'])
def wechat_auth():
    echostr = request.args.get('echostr', '')
    if verification():
        return make_response(echostr)
    return render_template("index.html")


@weixin.route('/', methods=['POST'])
def wechat_msg():
    rec = request.data
    msg = parse(rec)
    # from msg_handler import MsgHandler
    # message = MsgHandler(msg)
    if msg['MsgType'] == 'event':
        from msg_handler import handle_event
        content = handle_event(msg)
        return res_text_msg(msg, content)


@weixin.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@weixin.route('/code/<path:message_url>', methods=['GET', 'POST'])
def oauth(message_url):
    """
    这个函数用于获取微信公众号的文章链接并跳转
    :param message_url:公众号文章链接
    :return:跳转至相应链接
    """
    post_url = str(message_url).replace(':/', '://')
    post_url = post_url.replace('$', '?').replace('@', '#').replace('!', '&')
    code = request.args.get('code', '')
    if not code:
        return redirect(post_url)
    else:
        from nova_weixin.app.weixin.oauth_handler import get_openid
        openid = get_openid(code)
        try:
            from nova_weixin.app.weixin.oauth_handler import openid_handler
            openid_handler(openid, post_url)
        except:
            pass
        finally:
            return redirect(post_url)

# @weixin.route('/history', methods=['GET', 'POST'])
# def oauth_history():
#     """
#     这个函数微信自定义菜单链接的跳转
#     :return:跳转至相应链接
#     """
#     code = request.args.get('code', '')
#     return render_template('base2.html')
#     # if not code:
#     #     return redirect('http://www.njuszy.cn')
#     # else:
#     #     from nova_weixin.app.weixin.oauth_handler import get_openid
#     #     openid = get_openid(code)
#     #     #handle_history(openid)
#     #     return redirect('http://www.njuszy.cn')

#
# @weixin.route('/jiaowu')
# def oauth_jiaowu():
#     # code = request.args.get('code', '')
#     # if not code:
#     #     return redirect('')
#     # openid = get_openid(code)
#     openid = 'o19fSvhseI04YpNJkVYVIBTEjESs'
#     session['openid'] = openid
#     result = jiaowu(openid)
#     if result == -1:
#         return '您尚未绑定学号！'
#     if result:
#         session['email'] = result[0]
#         session['status'] = result[1]
#         session['stuid'] = result[2]
#         session['jiaowu'] = 'jiaowu'
#     return render_template('jiaowu.html')
#
#
# @weixin.route('/handle_jiaowu',methods=['GET','POST'])
# def handle_jiaowu():
#     if session['jiaowu'] == 'jiaowu' and request.args.get('num') == 1:
#         da = request.values
#         session['email'] = da.get('email')
#         session['status'] = da.get('status')
#         jiaowu_save(session['stuid'],session['email'],session['status'])
#     if request.args.get('num') == 2 and session['jiaowu'] == 'jiaowu':
#         return jsonify(result='ok',
#                        email=session['email'],
#                        status=session['status'])




def verification():
    """
    verify the weixin token
    """
    token = TOKEN
    data = request.args
    signature = data.get('signature', '')
    timestamp = data.get('timestamp', '')
    nonce = data.get('nonce', '')
    s = [timestamp, nonce, token]
    s.sort()
    s = ''.join(s)
    if hashlib.sha1(s).hexdigest() == signature:
        return 1
    return 0


def parse(rec):
    """
    :param rec: rec is a xml file
    :return: return a dictionary
    """
    root = ET.fromstring(rec)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

text_rep = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"


def res_text_msg(msg, content):
    response = make_response(text_rep % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), content))
    response.content_type = 'application/xml'
    return response
