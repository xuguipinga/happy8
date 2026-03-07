import re

def parse_sku(sku_string):
    """
    从销售 SKU 字符串中提取产品型号和规格。
    示例: "Color:Black-B002,Length:18cm" -> ("B002", "18cm")
    """
    if not sku_string:
        return None, None
    
    model = None
    spec = None
    
    # 1. 提取型号 (Model)
    # 规律：通常是大写字母开头，后面跟着数字，可能带有连字符，如 B001, B005-1, S1234
    # 排除常见的颜色词前缀
    model_regex = r'(?:^|[:\-\s,])([A-Z]\d{2,}(?:-[A-Z0-9]+)?)(?=$|[:\-\s,])'
    matches = re.findall(model_regex, sku_string)
    
    if matches:
        # 排除已知的非型号词（可选）
        model = matches[0]
    
    # 2. 提取规格 (Spec)
    # 规律：通常是类似 18cm, 20cm 或单选出的部分
    spec_regex = r'(?:Design|Length|Size)[:\s]+([^,\(\)]+)'
    spec_match = re.search(spec_regex, sku_string, re.IGNORECASE)
    if spec_match:
        spec = spec_match.group(1).strip()
    
    return model, spec

if __name__ == "__main__":
    # 测试用例
    test_skus = [
        "Color:B001,Design:20cm",
        "Color:Black-B001,Length:18cm",
        "Color:Black-B005-1,Length:18cm(7.09in)",
        "Color:Red,Size:Large-B010"
    ]
    for s in test_skus:
        m, sp = parse_sku(s)
        print(f"SKU: {s} => Model: {m}, Spec: {sp}")
