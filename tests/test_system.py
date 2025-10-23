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


def test_data_loader():
    """Test data loader functionality."""
    print("\n" + "="*60)
    print("TEST 1: DataLoader")
    print("="*60)
    
    try:
        loader = DataLoader(data_dir="data")
        print("✅ DataLoader initialized")
        
        # Test loading examples
        examples = loader.get_few_shot_examples(1, num_examples=3)
        print(f"✅ Retrieved examples for Agent 1")
        print(f"   Length: {len(examples)} characters")
        
        # Test stats
        stats = loader.get_dataset_stats(1)
        print(f"✅ Dataset 1 stats: {stats['total_examples']} examples")
        
        return True
    except Exception as e:
        print(f"❌ DataLoader test failed: {e}")
        return False


def test_specialist_analysis():
    """Test specialist analysis."""
    print("\n" + "="*60)
    print("TEST 2: Specialist Analysis")
    print("="*60)
    
    try:
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
        
        for report in reports:
            print(f"   Agent {report.agent_id} ({report.domain}): Score {report.preliminary_score:.1f}")
        
        return True
    except Exception as e:
        print(f"❌ Specialist analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_request_validation():
    """Test API request validation."""
    print("\n" + "="*60)
    print("TEST 3: API Request Validation")
    print("="*60)
    
    try:
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
        try:
            invalid_request = AnalysisRequest(
                responses=["Response 1", "Response 2"]
            )
            print("❌ Invalid request accepted (should have failed)")
            return False
        except:
            print("✅ Invalid request rejected correctly")
        
        return True
    except Exception as e:
        print(f"❌ Request validation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║          Sistema de Análise de Risco - Tests             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run tests
    results.append(("DataLoader", test_data_loader()))
    results.append(("API Validation", test_api_request_validation()))
    # Note: Specialist analysis test requires API key
    print("\n⚠️  Skipping specialist analysis test (requires GROQ_API_KEY)")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
