import yaml


__all__ = ("load_yaml",)


def sbin_to_int(s: str) -> int:
    return int(s.replace("\n", "").replace("\t", "").replace(" ", ""), 2)


def binary_loader(loader, node):
    value = loader.construct_scalar(node)
    return sbin_to_int(value)


yaml.add_constructor("!b", binary_loader)


def rev_binary_loader(loader, node):
    value = loader.construct_scalar(node)
    return sbin_to_int(value[::-1])


yaml.add_constructor("!rb", rev_binary_loader)


def load_yaml(fp):
    return yaml.load(fp, Loader=yaml.Loader)
