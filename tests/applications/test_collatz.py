import pytest

from tourbus.applications.collatz import collatz_orbit, collatz_stats


def test_orbit_of_one_is_just_one():
    assert list(collatz_orbit(1)) == [1]


def test_orbit_of_six():
    assert list(collatz_orbit(6)) == [6, 3, 10, 5, 16, 8, 4, 2, 1]


def test_famous_orbit_of_27():
    assert collatz_stats(27) == {"start": 27, "steps": 111, "max": 9232}


def test_stats_of_six():
    stats = collatz_stats(6)
    assert stats["steps"] == 8
    assert stats["max"] == 16
    assert stats["start"] == 6


def test_stats_of_one_is_zero_steps():
    assert collatz_stats(1) == {"start": 1, "steps": 0, "max": 1}


def test_every_orbit_reaches_one_up_to_1000():
    for n in range(1, 1001):
        orbit = list(collatz_orbit(n))
        assert orbit[0] == n
        assert orbit[-1] == 1


def test_stats_agree_with_orbit():
    for n in (7, 19, 97, 255):
        orbit = list(collatz_orbit(n))
        stats = collatz_stats(n)
        assert stats["steps"] == len(orbit) - 1
        assert stats["max"] == max(orbit)


def test_non_positive_start_rejected():
    with pytest.raises(ValueError):
        list(collatz_orbit(0))
    with pytest.raises(ValueError):
        collatz_stats(-5)
