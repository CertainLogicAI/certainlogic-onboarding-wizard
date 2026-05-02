"""Tests for CertainLogic Onboarding Wizard v2.0."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from onboarding_wizard import (
    OnboardingWizard, EnvironmentScanner,
    GOAL_PROFILES, CERTAINLOGIC_SKILLS, COMMUNITY_SKILLS
)


class TestEnvironmentScanner:
    """Test environment auto-detection."""

    def test_detect_os_linux(self):
        with patch('platform.system', return_value='Linux'):
            assert EnvironmentScanner.detect_os() == 'linux'

    def test_detect_os_macos(self):
        with patch('platform.system', return_value='Darwin'):
            assert EnvironmentScanner.detect_os() == 'macos'

    def test_scan_installed_skills(self, tmp_path):
        # Create mock skills directory
        (tmp_path / "skill-vetter-plus").mkdir()
        (tmp_path / "github").mkdir()

        installed = EnvironmentScanner.scan_installed_skills(tmp_path)
        assert "skill-vetter-plus" in installed
        assert "github" in installed
        assert len(installed) == 2

    def test_scan_no_skills_dir(self):
        result = EnvironmentScanner.scan_installed_skills(None)
        assert result == set()


class TestGoalDetection:
    """Test goal detection from user input."""

    def test_detect_developer(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("I'm a developer") == "developer"
        assert wizard.detect_goal("coding in python") == "developer"

    def test_detect_business(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("small business owner") == "business"
        assert wizard.detect_goal("startup") == "business"

    def test_detect_beginner(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("new to this") == "beginner"
        assert wizard.detect_goal("help me set up") == "beginner"

    def test_unknown_goal_defaults(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("xyzabc123") is None


class TestReportGeneration:
    """Test onboarding report generation."""

    def test_report_contains_skills(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "linux",
            "skills_dir": "/test/skills",
            "installed_skills": set(),
            "openclaw_version": "test"
        }
        report = wizard.generate_report("developer", env_info)
        assert "Skill Vetter Plus" in report
        assert "Smart Router" in report
        assert "clawhub install" in report

    def test_report_shows_installed_status(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "linux",
            "skills_dir": "/test/skills",
            "installed_skills": {"skill-vetter-plus"},
            "openclaw_version": "test"
        }
        report = wizard.generate_report("developer", env_info)
        assert "✅ Installed" in report or "already installed" in report

    def test_linux_skips_macos_only(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "linux",
            "skills_dir": "/test/skills",
            "installed_skills": set(),
            "openclaw_version": "test"
        }
        report = wizard.generate_report("productivity", env_info)
        assert "Things 3" in report  # Should show but note not supported
        assert "not supported" in report or "Skipped" in report or "macOS not supported" in report

    def test_macos_includes_things(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "macos",
            "skills_dir": "/test/skills",
            "installed_skills": set(),
            "openclaw_version": "test"
        }
        report = wizard.generate_report("productivity", env_info)
        assert "Things 3" in report
        assert "not supported" not in report.lower()


class TestHonesty:
    """Verify no false claims."""

    def test_no_auto_install_claims(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "linux",
            "skills_dir": None,
            "installed_skills": set(),
            "openclaw_version": "test"
        }
        report = wizard.generate_report("beginner", env_info)
        assert "auto-install" not in report.lower()
        assert "automatically installed" not in report.lower()

    def test_no_guaranteed_savings(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "linux",
            "skills_dir": None,
            "installed_skills": set(),
            "openclaw_version": "test"
        }
        report = wizard.generate_report("business", env_info)
        assert "guaranteed" not in report.lower()
        assert "100%" not in report or "NOT" in report  # Allow "NOT 100%"

    def test_disclaimer_present(self):
        wizard = OnboardingWizard()
        env_info = {
            "os": "linux",
            "skills_dir": None,
            "installed_skills": set(),
            "openclaw_version": "test"
        }
        report = wizard.generate_report("developer", env_info)
        assert "Verify before trusting" in report or "recommendations" in report.lower()


class TestProfileCoverage:
    """Every profile has at least one skill."""

    def test_all_profiles_have_skills(self):
        for goal, profile in GOAL_PROFILES.items():
            assert len(profile["certainlogic_skills"]) > 0, f"{goal} has no CertainLogic skills"

    def test_all_skill_refs_valid(self):
        for goal, profile in GOAL_PROFILES.items():
            for slug in profile["certainlogic_skills"]:
                assert slug in CERTAINLOGIC_SKILLS, f"Invalid skill ref: {slug}"
            for slug in profile.get("community_skills", []):
                assert slug in COMMUNITY_SKILLS, f"Invalid community ref: {slug}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
