
from app.utils.sku_parser import parse_sku

def test_parser():
    test_cases = [
        ("Color:B001,Design:20cm", "B001", "20cm"),
        ("Color:Black-B001,Length:18cm", "B001", "18cm"),
        ("Color:Black-B005-1,Length:18cm(7.09in)", "B005-1", "18cm"),
        ("Color:Red,Size:Large-B010", "B010", None),
        ("Color:Black,Size:22cm-B006", "B006", None),
        ("B123, 20cm", "B123", None),
    ]
    
    print("--- SKU Parser Verification ---")
    all_passed = True
    for sku, expected_model, expected_spec in test_cases:
        model, spec = parse_sku(sku)
        match = (model == expected_model)
        status = "PASS" if match else "FAIL"
        print(f"SKU: {sku:40} | Extracted: {str(model):10} | Expected: {str(expected_model):10} | Result: {status}")
        if not match:
            all_passed = False
    
    if all_passed:
        print("\n✅ All core patterns recognized correctly!")
    else:
        print("\n❌ Some patterns failed. Needs refinement.")

if __name__ == "__main__":
    test_parser()
