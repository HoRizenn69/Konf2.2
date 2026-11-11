"""Загрузка текста по HTTP(S) стандартной библиотекой."""

import ssl
import urllib.error
import urllib.request

from src.constants import (
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_TIMEOUT_SEC,
)

USER_AGENT = "cargo-graph-cli/0.2"


def fetch_text(url):
    """Скачивает URL и возвращает тело как строку UTF-8."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    try:
        return _open_and_decode(request, True)
    except urllib.error.HTTPError as err:
        _raise_http(err)
    except urllib.error.URLError as err:
        if _is_ssl_problem(err):
            return _fetch_insecure(request)
        raise ValueError(
            f"сеть недоступна: {err.reason}"
        ) from err


def _fetch_insecure(request):
    """Повторный запрос без проверки SSL-сертификата."""
    try:
        return _open_and_decode(request, False)
    except urllib.error.HTTPError as err:
        _raise_http(err)
    except urllib.error.URLError as err:
        raise ValueError(
            f"сеть недоступна: {err.reason}"
        ) from err


def _open_and_decode(request, verified):
    """Открывает URL и декодирует ответ в UTF-8."""
    context = _make_ssl_context(verified)
    with urllib.request.urlopen(
        request,
        timeout=HTTP_TIMEOUT_SEC,
        context=context,
    ) as response:
        code = response.getcode()
        if code != HTTP_OK:
            raise ValueError(
                f"неожиданный HTTP-код: {code}"
            )
        raw = response.read()
        return raw.decode("utf-8")


def _make_ssl_context(verified):
    """Создаёт SSL-контекст с проверкой или без неё."""
    if verified:
        return ssl.create_default_context()
    return ssl._create_unverified_context()


def _is_ssl_problem(err):
    """Проверяет, связана ли ошибка с SSL/сертификатом."""
    text = str(err).lower()
    if "ssl" in text:
        return True
    return "certificate" in text


def _raise_http(err):
    """Преобразует HTTPError в понятный ValueError."""
    if err.code == HTTP_NOT_FOUND:
        raise ValueError(
            "пакет не найден в репозитории"
        ) from err
    raise ValueError(
        f"ошибка HTTP {err.code}: {err.reason}"
    ) from err
