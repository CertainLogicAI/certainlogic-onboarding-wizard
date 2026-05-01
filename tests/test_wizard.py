"""Quick tests for Onboarding Wizard."""
import pytest
from pathlib import Path
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from onboarding_wizard import OnboardingWizard, GOAL_PROFILES


class TestGoalDetection:
    """Test goal detection from free-form input."""

    def test_detect_developer(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("I'm a developer") == "developer"
        assert wizard.detect_goal("I code in Python") == "developer"
        assert wizard.detect_goal("programming") == "developer"

    def test_detect_business(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("small business") == "business"
        assert wizard.detect_goal("startup") == "business"

    def test_detect_beginner(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("new to this") == "beginner"

    def test_unknown_goal(self):
        wizard = OnboardingWizard()
        assert wizard.detect_goal("xyzabc123") is None


class TestGuideGeneration:
    """Test markdown guide generation."""

    def test_guide_contains_disclaimer(self):
        wizard = OnboardingWizard()
        guide = wizard.generate_guide("developer", ["Python", "yes", "solo", "50"])
        assert "recommendation only" in guide
        assert "Verify everything before trusting" in guide

    def test_guide_has_skills(self):
        wizard = OnboardingWizard()
        guide = wizard.generate_guide("beginner", ["", "", "", ""])
        assert "Skill Vetter Plus" in guide
        assert "Install:" in guide

    def test_guide_saves_correctly(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = OnboardingWizard(output_dir=tmpdir)
            guide = wizard.generate_guide("productivity", ["macOS", "Things 3", "email", "organize"])
            path = wizard.save_guide(guide, filename="test-guide.md")
            assert path.exists()
            assert "Personal Assistant Pack" in path.read_text()


class TestHonesty:
    """Ensure no false claims in output."""

    def test_no_auto_install_claims(self):
        wizard = OnboardingWizard()
        for goal in GOAL_PROFILES:
            guide = wizard.generate_guide(goal, ["", "", "", ""])
            assert "auto-install" not in guide.lower() or "does NOT" in guide
            assert "100%" not in guide
            assert "guaranteed" not in guide.lower()

    def test_caveats_present(self):
        wizard = OnboardingWizard()
        guide = wizard.generate_guide("developer", ["", "", "", ""])
        assert "Caveat:" in guide or "caveat" in guide.lower()
        assert "Limitations" in guide or "limitations" in guide.lower()

    def test_no_percent_savings(self):
        wizard = OnboardingWizard()
        guide = wizard.generate_guide("business", ["", "", "", ""])
        # No specific percent claims like "45-65% savings"
        import re
        percentages = re.findall(r'\d+%', guide)
        assert len(percentages) == 0 or all(int(p[:-1]) < 100 for p in percentages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
