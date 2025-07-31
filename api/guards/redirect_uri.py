import re
from fastapi import Header
from schemas.http_exception import BadRequestException
from configs.oauth import ROOT_SERVICE_ORIGIN, GOOGLE_ROOT_REDIRECT_URI, GOOGLE_INSTANCE_REDIRECT_PATH

def get_redirect_uri(referer: str | None = Header(None)) -> str:
    """
    oauthのredirect_uriとアプリケーションがクロスオリジンになってCookieの書き込みに失敗するので、無理やりアプリケーションのオリジンにつなぐ
    初回のリクエストはrefererヘッダからoriginを抽出し、このapiのデプロイ先であればそのまま、違うなら指定したプロキシパスを使う
        （originヘッダはsame siteの場合省略されることがあるのでrefererを用いる）
    リダイレクト後（/user/login/google/callbackなど）はアプリケーションにリダイレクトするための`redirect_to`パラメータを使い、originをパースする
    `redirect_to`がoriginを含んだurlではなく`/`から始まるpathだった場合はapiのデプロイ先のものを使う
    """
    origin_match = re.match(r"^(https?://[^/]+)", referer if referer is not None else ROOT_SERVICE_ORIGIN)
    if origin_match:
        redirect_origin = origin_match.group(0)
        print(redirect_origin == ROOT_SERVICE_ORIGIN)
        if redirect_origin != ROOT_SERVICE_ORIGIN:
            return f"{redirect_origin}{GOOGLE_INSTANCE_REDIRECT_PATH}"
        else:
            return GOOGLE_ROOT_REDIRECT_URI
    elif referer.startswith("/"):
        return GOOGLE_ROOT_REDIRECT_URI
    else:
        raise BadRequestException("Invalid uri")
