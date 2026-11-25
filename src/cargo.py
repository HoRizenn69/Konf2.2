"""Прямые зависимости Cargo через API crates.io."""

import json
from urllib.parse import quote

from src.constants import EMPTY_COUNT, KIND_NORMAL
from src.http_fetch import fetch_text


def fetch_cargo_deps(repo, package):
    """Возвращает пары (crate, требование) для пакета."""
    version = _stable_version(repo, package)
    url = build_deps_url(repo, package, version)
    payload = _load_json(url)
    return parse_direct_deps(payload)


def build_crate_url(repo, package):
    """Строит URL карточки crate."""
    base = repo.rstrip("/")
    name = quote(package.lower(), safe="")
    return f"{base}/crates/{name}"


def build_deps_url(repo, package, version):
    """Строит URL списка зависимостей версии."""
    base = repo.rstrip("/")
    name = quote(package.lower(), safe="")
    ver = quote(version, safe="")
    return (
        f"{base}/crates/{name}/"
        f"{ver}/dependencies"
    )


def parse_direct_deps(data):
    """Возвращает normal-зависимости без optional и дублей."""
    items = _dependency_items(data)
    found = []
    seen = set()
    for item in items:
        pair = _normal_dep(item)
        if pair is None:
            continue
        if pair[0] in seen:
            continue
        seen.add(pair[0])
        found.append(pair)
    return found


def read_stable_version(data):
    """Берёт max_stable_version, иначе max_version."""
    crate = _crate_object(data)
    version = _version_field(
        crate,
        "max_stable_version",
    )
    if version is None:
        version = _version_field(crate, "max_version")
    if version is None:
        raise ValueError(
            "не найдена актуальная версия пакета"
        )
    return version


def _stable_version(repo, package):
    """Загружает актуальную stable-версию crate."""
    url = build_crate_url(repo, package)
    payload = _load_json(url)
    return read_stable_version(payload)


def _load_json(url):
    """Скачивает URL и разбирает JSON-объект."""
    text = fetch_text(url)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise ValueError(
            f"некорректный JSON: {err}"
        ) from err
    if not isinstance(data, dict):
        raise ValueError("ожидался JSON-объект")
    return data


def _crate_object(data):
    """Достаёт объект crate из ответа API."""
    if not isinstance(data, dict):
        raise ValueError("некорректный ответ crates.io")
    crate = data.get("crate")
    if not isinstance(crate, dict):
        raise ValueError("в ответе нет объекта crate")
    return crate


def _version_field(crate, key):
    """Возвращает непустую строку версии или None."""
    value = crate.get(key)
    if not isinstance(value, str):
        return None
    value = value.strip()
    if len(value) == EMPTY_COUNT:
        return None
    return value


def _dependency_items(data):
    """Возвращает список зависимостей из ответа API."""
    if not isinstance(data, dict):
        raise ValueError("некорректный ответ зависимостей")
    items = data.get("dependencies")
    if items is None:
        raise ValueError(
            "в ответе нет поля dependencies"
        )
    if not isinstance(items, list):
        raise ValueError(
            "поле dependencies должно быть списком"
        )
    return items


def _normal_dep(item):
    """Возвращает пару для normal-зависимости или None."""
    if not isinstance(item, dict):
        return None
    if item.get("kind") != KIND_NORMAL:
        return None
    if item.get("optional"):
        return None
    name = _dep_name(item)
    if name is None:
        return None
    return (name, _dep_req(item))


def _dep_name(item):
    """Читает имя crate из элемента зависимости."""
    name = item.get("crate_id")
    if not isinstance(name, str):
        return None
    name = name.strip()
    if len(name) == EMPTY_COUNT:
        return None
    return name


def _dep_req(item):
    """Читает требование версии или пустую строку."""
    req = item.get("req")
    if not isinstance(req, str):
        return ""
    return req.strip()
