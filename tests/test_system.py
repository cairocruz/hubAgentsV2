"""
Test script to validate the complete system.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import AnalysisRequest
from utils.data_loader import DataLoader
from agents.specialist_analysis import run_specialist_analysis_sync
import pytest

def test_data_loader():
    """Test data loader functionality."""
    print("\n" + "="*60)
    print("TEST 1: DataLoader")
    print("="*60)
    
    loader = DataLoader(data_dir="data")
    print("✅ DataLoader initialized")

    # Test loading examples
    examples = loader.get_few_shot_examples(1, num_examples=3)
    print(f"✅ Retrieved examples for Agent 1")
    print(f"   Length: {len(examples)} characters")
    assert len(examples) > 0

    # Test stats
    stats = loader.get_dataset_stats(1)
    print(f"✅ Dataset 1 stats: {stats['total_examples']} examples")
    assert stats['total_examples'] > 0


def test_specialist_analysis():
    """Test specialist analysis."""
    print("\n" + "="*60)
    print("TEST 2: Specialist Analysis")
    print("="*60)
    
    # This test requires an API key, so we'll skip it if the key is not available.
    if not os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_OPENAI_ENDPOINT"):
        pytest.skip("Skipping specialist analysis test (requires API key)")

    loader = DataLoader(data_dir="data")
    
    test_responses = [
        "Eu faço tudo em casa sozinha enquanto ele só assiste TV.",
        "Ele grita comigo quando não gosta de algo.",
        "Parei de ver minhas amigas porque ele não gosta.",
        "Ele controla todo o dinheiro da casa.",
        "Tenho me sentido muito cansada ultimamente."
    ]
    
    print("Running specialist analysis...")
    reports = run_specialist_analysis_sync(test_responses, loader)
    
    print(f"✅ Generated {len(reports)} specialist reports")
    assert len(reports) == 5
    
    for report in reports:
        print(f"   Agent {report.agent_id} ({report.domain}): Score {report.preliminary_score:.1f}")
        assert report.preliminary_score >= 0 and report.preliminary_score <= 100


def test_api_request_validation():
    """Test API request validation."""
    print("\n" + "="*60)
    print("TEST 3: API Request Validation")
    print("="*60)
    
    # Valid request
    valid_request = AnalysisRequest(
        responses=[
            "Response 1",
            "Response 2",
            "Response 3",
            "Response 4",
            "Response 5"
        ]
    )
    print("✅ Valid request accepted")
    
    # Invalid request (less than 5)
    with pytest.raises(Exception):
        invalid_request = AnalysisRequest(
            responses=["Response 1", "Response 2"]
        )
    print("✅ Invalid request rejected correctly")
