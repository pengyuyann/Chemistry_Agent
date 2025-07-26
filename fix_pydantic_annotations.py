#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量修复Pydantic类型注解问题的脚本
"""

import os
import re

def fix_file_annotations(file_path):
    """修复单个文件中的类型注解问题"""
    print(f"正在修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复name和description字段的类型注解
    # 匹配模式：name = "..." 或 description = "..."
    patterns = [
        (r'(\s+)name\s*=\s*"([^"]+)"', r'\1name: str = "\2"'),
        (r'(\s+)description\s*=\s*"([^"]+)"', r'\1description: str = "\2"'),
        (r'(\s+)name\s*=\s*\'([^\']+)\'', r'\1name: str = \'\2\''),
        (r'(\s+)description\s*=\s*\'([^\']+)\'', r'\1description: str = \'\2\'')
    ]
    
    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已修复: {file_path}")
    else:
        print(f"- 无需修复: {file_path}")

def main():
    """主函数"""
    # 需要修复的文件列表
    files_to_fix = [
        'app/core/tools/rdkit.py',
        'app/core/tools/reactions.py',
        'app/core/tools/rxn4chem.py',
        'app/core/tools/safety.py',
        'app/core/tools/search.py',
        'app/core/tools/converters.py',
        'app/core/tools/chemspace.py',
        'app/core/tools/human_feedback.py',
        'app/core/tools/reranker_tool.py',
        'chemcrow/tools/rdkit.py',
        'chemcrow/tools/reactions.py',
        'chemcrow/tools/rxn4chem.py',
        'chemcrow/tools/safety.py',
        'chemcrow/tools/search.py',
        'chemcrow/tools/converters.py',
        'chemcrow/tools/chemspace.py'
    ]
    
    print("开始批量修复Pydantic类型注解...")
    print("=" * 60)
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_file_annotations(file_path)
        else:
            print(f"⚠ 文件不存在: {file_path}")
    
    print("=" * 60)
    print("批量修复完成！")

if __name__ == "__main__":
    main() 