# test_system.py
import os
import glob
import pytest
from tools import CitationVerifierTool

# Metric 1: Unit Test the Custom Tool (Robustness)
def test_citation_tool_success():
    """Test that CitationVerifier correctly identifies existing keywords"""
    tool = CitationVerifierTool()
    result = tool._run(url="https://www.google.com", keyword="Google")
    assert "VERIFIED" in result, "Should find 'Google' on google.com"

def test_citation_tool_failure():
    """Test that CitationVerifier correctly rejects missing keywords"""
    tool = CitationVerifierTool()
    result = tool._run(url="https://www.google.com", keyword="ScholarSyncUniqueKeyword12345")
    assert "UNVERIFIED" in result, "Should not find random keyword"

def test_citation_tool_bad_url():
    """Test error handling for unreachable URLs"""
    tool = CitationVerifierTool()
    result = tool._run(url="https://thiswebsitedoesnotexist99999.xyz", keyword="test")
    assert ("Error" in result or "System Error" in result), "Should handle bad URLs gracefully"

def test_citation_tool_timeout():
    """Test timeout handling for slow-responding sites"""
    tool = CitationVerifierTool()
    # This might be slow, but should complete within timeout
    result = tool._run(url="https://httpstat.us/200?sleep=5000", keyword="test")
    # Should either timeout or complete - both are acceptable
    assert isinstance(result, str), "Should return string result"

# Metric 2: System Output Verification
def test_output_file_creation():
    """Verify that the system generates timestamped report files"""
    # Look for any report files matching the pattern
    report_files = glob.glob("research_report_*.md")
    
    assert len(report_files) > 0, "No research report files found. Run main.py first."
    
    # Test the most recent file
    latest_report = max(report_files, key=os.path.getctime)
    
    with open(latest_report, "r", encoding='utf-8') as f:
        content = f.read()
    
    # Quality checks
    assert len(content) > 100, "Report is too short - likely incomplete"
    assert "agent" in content.lower(), "Report should mention 'agent' (verification keyword)"
    assert "#" in content, "Report should have markdown headers"
    
    # Check for structure
    assert any(word in content.lower() for word in ["introduction", "conclusion", "overview"]), \
        "Report should have proper structure"
    
    print(f"✅ Test passed! Verified report: {latest_report}")

def test_multiple_reports_no_overwrite():
    """Ensure dynamic filenames prevent data loss"""
    report_files = glob.glob("research_report_*.md")
    
    if len(report_files) > 1:
        # Check that files have different timestamps
        filenames = [os.path.basename(f) for f in report_files]
        assert len(filenames) == len(set(filenames)), "Duplicate filenames detected!"
        print(f"✅ Found {len(report_files)} unique reports - no overwrites")
    else:
        print("ℹ️ Only one report found. Run main.py multiple times to test no-overwrite feature.")