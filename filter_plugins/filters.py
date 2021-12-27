"""Custom Jinja filters for Ansible."""
from ipaddress import ip_network
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Union

from ansible.errors import AnsibleFilterTypeError


__all__ = ('FilterModule',)


class FilterModule:
    """Ansible plugin class for filters."""
    def filters(self) -> dict[str, Callable[..., Any]]:
        """Return a dict of custom filters."""
        return {
            'cidrsort': cidrsort,
            'dnssort': dnssort,
            'pathiter': pathiter,
            'walk': walk,
        }


def cidrsort(
    data: Any,
) -> list[str]:
    """Sort a list of IP addresses or networks."""
    if not isinstance(data, list) or not all(isinstance(i, str) for i in data):
        raise AnsibleFilterTypeError('cidrsort can only be used on lists of strings')

    data.sort(key=cidr_key)
    return data


def cidr_key(
    cidr: str,
) -> tuple[int, int, int]:
    """Key for cidrsort."""
    network = ip_network(cidr)
    return (network.version, int(network.network_address), network.prefixlen)


def dnssort(
    data: Any,
) -> list[str]:
    """Sort a list of domains by DNS labels in reverse order skipping the TLD."""
    if not isinstance(data, list) or not all(isinstance(i, str) for i in data):
        raise AnsibleFilterTypeError('dnssort can only be used on lists of strings')

    data.sort(key=dns_key)
    return data


def dns_key(
    domain: str,
    skip_suffix: bool = True,
) -> list[str]:
    """Return the labels of the DNS domain in reverse order for sorting."""
    parts = domain.rstrip('.').split('.')
    if skip_suffix:
        parts = parts[:-1]
    parts.reverse()
    return parts


def pathiter(
    data: Any,
    start: int = 0,
    stop: Optional[int] = None,
) -> list[str]:
    """Return a list containing each segment of a path."""
    if not isinstance(data, str):
        raise AnsibleFilterTypeError('pathiter can only be used on a string')

    parts = data.split('/')
    if stop is not None:
        parts = parts[:stop]
    return ['/'.join(parts[:i]) for i in range(start, len(parts) + 1)]


def walk(
    data: Any,
    path: Union[str, Sequence[str]],
    labels: Optional[Sequence[str]] = None,
) -> Iterable[dict[str, Any]]:
    """Recurse over objects in data matching path."""
    if labels and any(label in ('keys', 'value') for label in labels):
        raise ValueError('Invalid label')

    if isinstance(path, str):
        path = path.split('.')

    for keys, value in _walk(data, path, ()):
        item = {
            'keys': keys,
            'value': value,
        }
        if labels:
            item |= {
                label: keys[i] for i, label in enumerate(labels)
                if label
            }

        yield item


Keys = tuple[Any, ...]


def _walk(
    data: Any,
    path: Sequence[str],
    keys: Keys,
) -> Iterable[tuple[Keys, Any]]:
    """Handle a step in path and then recurse."""
    step = path[0] if path else None

    if step is None:
        yield (keys, data)

    elif step == '*':
        iterator: Iterable[tuple[Any, Any]]
        if isinstance(data, list):
            iterator = enumerate(data)
        elif isinstance(data, dict):
            iterator = data.items()
        else:
            raise AnsibleFilterTypeError('* step on neither list nor dict')

        for key, value in iterator:
            yield from _walk(value, path[1:], keys + (key,))

    else:
        if step not in data:
            return
        yield from _walk(data[step], path[1:], keys)
