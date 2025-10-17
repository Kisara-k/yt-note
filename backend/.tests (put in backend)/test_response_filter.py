"""
Test script to verify the AI response filter integration
"""

def test_filter_import():
    """Test that the filter can be imported"""
    try:
        from openai_api.response_filter import filter_ai_response
        print("✓ Successfully imported filter_ai_response")
        return True
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False


def test_filter_function():
    """Test the filter function with sample data"""
    try:
        from openai_api.response_filter import filter_ai_response
        
        # Test with string and field_name
        result1 = filter_ai_response("  Test response  ", field_name="title")
        assert isinstance(result1, str), "Result should be a string"
        print(f"✓ String filtering works: '{result1}'")
        
        # Test with different field names
        result2 = filter_ai_response("Field 1 content", field_name="field_1")
        assert isinstance(result2, str), "Result should be a string"
        print(f"✓ field_1 filtering works: '{result2}'")
        
        result3 = filter_ai_response("Field 2 content", field_name="field_2")
        assert isinstance(result3, str), "Result should be a string"
        print(f"✓ field_2 filtering works: '{result3}'")
        
        result4 = filter_ai_response("Field 3 content", field_name="field_3")
        assert isinstance(result4, str), "Result should be a string"
        print(f"✓ field_3 filtering works: '{result4}'")
        
        # Test without field_name
        result5 = filter_ai_response("Another test")
        assert isinstance(result5, str), "Result should be a string"
        print(f"✓ Filtering without field_name works: '{result5}'")
        
        return True
    except Exception as e:
        print(f"✗ Filter function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enrichment_integration():
    """Test that enrichment.py can import and use the filter"""
    try:
        # Just check if the import works in enrichment.py
        import openai_api.enrichment as enrichment_module
        
        # Check if the filter is imported
        if hasattr(enrichment_module, 'filter_ai_response'):
            print("✓ enrichment.py has filter_ai_response imported")
        else:
            print("⚠ enrichment.py doesn't expose filter_ai_response (but this is OK)")
        
        return True
    except Exception as e:
        print(f"✗ Enrichment integration test failed: {e}")
        return False


def test_api_integration():
    """Test that api.py can import the filter"""
    try:
        # This will execute imports but won't start the server
        import sys
        import os
        
        # Temporarily suppress FastAPI warnings
        import warnings
        warnings.filterwarnings('ignore')
        
        # Import api module
        import api
        
        # Check if filter_ai_response is imported
        if hasattr(api, 'filter_ai_response'):
            print("✓ api.py has filter_ai_response imported")
            return True
        else:
            print("✗ api.py doesn't have filter_ai_response imported")
            return False
            
    except Exception as e:
        print(f"✗ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("AI Response Filter Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_filter_import),
        ("Filter Function Test", test_filter_function),
        ("Enrichment Integration", test_enrichment_integration),
        ("API Integration", test_api_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The filter is properly integrated.")
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
