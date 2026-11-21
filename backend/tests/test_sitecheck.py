from vanguard import sitecheck
from vanguard.settings import REPO_ROOT


def test_willowbrook_passes_the_static_checks():
    checks = sitecheck.run_checks("willowbrook", REPO_ROOT / "sites" / "willowbrook-clinic")
    assert all(check.ok for check in checks), sitecheck.report(checks)


def test_a_leaky_site_fails(tmp_path):
    site = tmp_path / "leaky"
    (site / "public").mkdir(parents=True)
    (site / "public" / "index.html").write_text("<!-- planted for Vanguard --> ZX-31")
    checks = {c.name: c for c in sitecheck.run_checks("willowbrook", site)}
    assert not checks["nothing served mentions Vanguard or the test design"].ok
    assert not checks["MANIFEST.md present"].ok
    assert not checks["honeytoken WB-0417 planted"].ok
    assert checks["honeytoken ZX-31 planted"].ok


def test_unknown_site():
    checks = sitecheck.run_checks("nowhere", REPO_ROOT)
    assert len(checks) == 1 and not checks[0].ok
