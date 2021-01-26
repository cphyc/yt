import warnings
from typing import List


class VisibleDeprecationWarning(UserWarning):
    """Visible deprecation warning, adapted from NumPy

    The nose runner does not show users DeprecationWarning.
    This ensures that a deprecation warning is visible to users
    if that is desired.
    """

    # this class becomes useless after the tests are migrated from nose to pytest

    pass


class WarnOnce:
    def __init__(self):
        self._warned = False

    def __call__(self, silenced_warnings: List[str]):
        if self._warned:
            return

        msg = "The following warnings have been silenced in the config file: "
        msg += "[" + ", ".join(silenced_warnings) + "]"
        warnings.warn(msg, UserWarning, stacklevel=3)
        self._warned = True


warn_about_silenced_warnings = WarnOnce()


def issue_deprecation_warning(
    msg, *, removal, since=None, stacklevel=3, deprecation_id=None, prevent_ignore=False
):
    """
    Parameters
    ----------
    msg: str
        A text message explaining that the code surrounding the call to this function is
        deprecated, and what should be changed on the user side to avoid it.

    deprecation_id: str
        A unique id to identify the deprecation message. This can be used to silent
        some warnings manually.

    prevent_ignore: bool
        If True, this deprecation warning won't be ignored. This is also useful at places
        where yt's config hasn't been read (yet).

    since and removal: str version numbers, indicating the anticipated removal date

    Crucial note:
    beware that `removal` is required (it doesn't have a default value). This is
    vital since deprecated code is typically untested and not specifying a required
    keyword argument will turn the warning into a TypeError.
    What it gets us however is that the release manager will know for a fact wether it
    is safe to remove a feature at any given point, and users have a better idea when
    their code will become incompatible.

    `since` is optional only because it was introduced in the 4.0.0 release, and it
    should become mandatory in the future.
    Both `since` and `removal` are keyword-only arguments so that their order can be
    swapped in the future without introducing bugs.

    Examples
    --------
    >>> issue_deprecation_warning(
            "This code is deprecated.",
            deprecation_id="filename:key",
            since="4.0.0",
            removal="4.2.0"
        )
    """
    if not prevent_ignore:
        # We need to import this here to prevent import cycles
        from yt.config import ytcfg

        silenced_warnings = ytcfg.get("yt", "developers", "ignore_warnings")
        if deprecation_id in silenced_warnings:
            warn_about_silenced_warnings(silenced_warnings)
            return

    msg += "\n"
    if since is not None:
        msg += f"Deprecated since v{since} . "

    msg += f"This feature will be removed in v{removal}"
    warnings.warn(msg, VisibleDeprecationWarning, stacklevel=stacklevel)
