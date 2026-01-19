import os

try:
    import requests
except Exception:
    requests = None

LANG_MAP = {'kg': 'ky', 'ru': 'ru', 'en': 'en'}


def translate_text(text, target_lang, provider='libre', api_url=None, timeout=10):
    """Translate text using LibreTranslate (default). Returns translated text or empty string on error."""
    if not text:
        return ''
    if provider != 'libre':
        raise NotImplementedError('Only libre provider implemented')
    if requests is None:
        raise RuntimeError('requests library is required for translation. Install it with pip install requests')
    t = LANG_MAP.get(target_lang, target_lang)
    url = api_url or os.environ.get('LIBRETRANSLATE_URL', 'https://libretranslate.com/translate')
    try:
        resp = requests.post(url, data={'q': text, 'source': 'auto', 'target': t, 'format': 'text'}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get('translatedText', '') or ''
    except Exception:
        return ''
