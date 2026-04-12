from __future__ import annotations
from ageoa.ghost.abstract import AbstractArray, AbstractDistribution, AbstractScalar, AbstractSignal
def witness_isleapyear(year: AbstractArray, *args, **kwargs) -> AbstractArray:
    """Shape-and-type check for isleapyear. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=year.shape,
        dtype="float64",
    )
    return result

def witness_find_dayinyear(month: AbstractArray, day: AbstractArray, isleap: AbstractArray) -> AbstractArray:
    """Shape-and-type check for find dayinyear. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=month.shape,
        dtype="float64",
    )
    return result

def witness_find_year(d: AbstractArray) -> AbstractArray:
    """Shape-and-type check for find year. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=d.shape,
        dtype="float64",
    )
    return result

def witness_find_month(dayinyear: AbstractArray, isleap: AbstractArray) -> AbstractArray:
    """Shape-and-type check for find month. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=dayinyear.shape,
        dtype="float64",
    )
    return result

def witness_find_day(dayinyear: AbstractArray, month: AbstractArray, isleap: AbstractArray) -> AbstractArray:
    """Shape-and-type check for find day. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=dayinyear.shape,
        dtype="float64",
    )
    return result

def witness_lastj2000dayofyear(year: AbstractArray) -> AbstractArray:
    """Shape-and-type check for lastj2000 dayofyear. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=year.shape,
        dtype="float64",
    )
    return result

def witness_hms2fd(h: AbstractArray, m: AbstractArray, s: AbstractArray) -> AbstractArray:
    """Shape-and-type check for hms2 fd. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=h.shape,
        dtype="float64",
    )
    return result

def witness_fd2hms(fd: AbstractArray) -> AbstractArray:
    """Shape-and-type check for fd2 hms. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=fd.shape,
        dtype="float64",
    )
    return result

def witness_fd2hmsf(fd: AbstractArray) -> AbstractArray:
    """Shape-and-type check for fd2 hmsf. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=fd.shape,
        dtype="float64",
    )
    return result

def witness_cal2jd(Y: AbstractArray, M: AbstractArray, D: AbstractArray) -> AbstractArray:
    """Shape-and-type check for cal2 jd. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=Y.shape,
        dtype="float64",
    )
    return result

def witness_calhms2jd(Y: AbstractArray, M: AbstractArray, D: AbstractArray, h: AbstractArray, m: AbstractArray, sec: AbstractArray) -> AbstractArray:
    """Shape-and-type check for calhms2 jd. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=Y.shape,
        dtype="float64",
    )
    return result

def witness_jd2cal(dj1: AbstractArray, dj2: AbstractArray) -> AbstractArray:
    """Shape-and-type check for jd2 cal. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=dj1.shape,
        dtype="float64",
    )
    return result

def witness_jd2calhms(dj1: AbstractArray, dj2: AbstractArray) -> AbstractArray:
    """Shape-and-type check for jd2 calhms. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=dj1.shape,
        dtype="float64",
    )
    return result

def witness_utc2tai(utc1: AbstractArray, utc2: AbstractArray) -> AbstractArray:
    """Shape-and-type check for utc2 tai. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=utc1.shape,
        dtype="float64",
    )
    return result

def witness_tai2utc(tai1: AbstractArray, tai2: AbstractArray) -> AbstractArray:
    """Shape-and-type check for tai2 utc. Returns output metadata without running the real computation."""
    result = AbstractArray(
        shape=tai1.shape,
        dtype="float64",
    )
    return result